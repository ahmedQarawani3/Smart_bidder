
from decimal import Decimal, InvalidOperation
from .models import FeasibilityStudy
from investor.models import InvestmentOffer, Negotiation

def calculate_detailed_project_analysis(project_id):
    try:
        fs = FeasibilityStudy.objects.get(project_id=project_id)
    except FeasibilityStudy.DoesNotExist:
        return {"error": "No feasibility study found for this project."}

    readiness = fs.project.readiness_level

    # ===== 1. Market Potential =====
    if readiness == "idea":
        market_potential = 40
    elif readiness == "prototype":
        market_potential = 60
    else:
        try:
            revenue_str = fs.expected_monthly_revenue.replace(',', '').strip()
            expected_revenue = float(revenue_str)
        except (ValueError, AttributeError):
            expected_revenue = 0

        growth_factor = 20 if fs.growth_opportunity and len(fs.growth_opportunity) > 30 else 5
        market_potential = min(100, (expected_revenue / 1000) + growth_factor)

    # ===== 2. Risk Assessment =====
    if readiness == "idea":
        risk_assessment = 80
    elif readiness == "prototype":
        risk_assessment = 50
    else:
        try:
            funding_required = float(fs.funding_required)
        except (ValueError, TypeError):
            funding_required = 0
        try:
            current_revenue = float(fs.current_revenue) if fs.current_revenue is not None else 0
        except (ValueError, TypeError):
            current_revenue = 0

        risk = fs.roi_period_months * 2

        if current_revenue > 0:
            ratio = funding_required / current_revenue
            risk += min(30, ratio * 10)
        else:
            risk += 30

        risk_assessment = min(100, risk)

    # ===== 3. Competitive Edge =====
    if readiness == "idea":
        competitive_edge = 30
    elif readiness == "prototype":
        competitive_edge = 50
    else:
        team_score = (fs.team_investment_percentage + fs.marketing_investment_percentage) / 2
        offers_count = InvestmentOffer.objects.filter(project=fs.project).count()
        negotiations_count = Negotiation.objects.filter(offer__project=fs.project).count()

        competitive_edge = min(100, team_score + offers_count * 2 + negotiations_count * 1)

    # ===== 4. Overall Score =====
    overall_score = (
        market_potential * 0.4 +
        competitive_edge * 0.4 -
        risk_assessment * 0.2
    )
    overall_score = max(0, min(100, overall_score))

    fs.market_potential = round(market_potential, 2)
    fs.risk_assessment = round(risk_assessment, 2)
    fs.competitive_edge = round(competitive_edge, 2)
    fs.overall_score = round(overall_score, 2)
    fs.save()

    return {
        "overall_score": fs.overall_score,
        "market_potential": fs.market_potential,
        "risk_assessment": fs.risk_assessment,
        "competitive_edge": fs.competitive_edge,
    }


def calculate_roi_forecast(project_id):
    try:
        fs = FeasibilityStudy.objects.get(project_id=project_id)
    except FeasibilityStudy.DoesNotExist:
        return {"error": "No feasibility study found for this project."}

    expected_revenue = clean_expected_revenue(fs.expected_monthly_revenue)
    funding_required = float(fs.funding_required or 0)
    roi_months = fs.roi_period_months

    if expected_revenue == 0 or funding_required == 0:
        return {
            "roi_forecast": "⚠️ لا يمكن حساب العائد، الإيرادات المتوقعة أو التمويل غير متوفر أو صفر."
        }

    monthly_roi = expected_revenue / funding_required
    total_return = monthly_roi * roi_months

    if total_return >= 2:
        message = "✅ العائد المتوقع جيد، يتجاوز ضعف التمويل خلال فترة الاسترداد."
    elif total_return >= 1:
        message = "⚠️ العائد معقول، يساوي أو يقترب من التمويل."
    else:
        message = "❌ العائد منخفض، قد لا يكون المشروع مربحًا خلال الفترة المحددة."

    return {
        "roi_forecast": message,
        "monthly_roi_ratio": round(monthly_roi, 2),
        "expected_total_return": round(total_return, 2)
    }

import re

def clean_expected_revenue(value):
    if not value:
        return 0
    try:
        # التقاط أول رقم عشري أو صحيح من النص
        match = re.search(r"[\d,]+(\.\d+)?", value)
        if match:
            number = match.group(0).replace(",", "")
            return float(number)
        return 0
    except:
        return 0
from .models import FeasibilityStudy

def calculate_investment_distribution(project_id):
    try:
        fs = FeasibilityStudy.objects.get(project_id=project_id)
    except FeasibilityStudy.DoesNotExist:
        return {"error": "No feasibility study found for this project."}

    team = fs.team_investment_percentage
    marketing = fs.marketing_investment_percentage

    total = team + marketing
    if total == 0:
        return {
            "investment_distribution": "⚠️ No investment distribution specified for team or marketing."
        }

    diff = abs(team - marketing)

    if diff <= 10:
        recommendation = "✅ The investment between the team and marketing is balanced. This is a good sign."
    elif team > marketing:
        recommendation = "👥 More investment is directed toward the team. Consider boosting marketing investment to increase market reach."
    else:
        recommendation = "📢 More investment is directed toward marketing. Ensure the team can handle the expected growth."

    return {
        "team_percentage": team,
        "marketing_percentage": marketing,
        "investment_distribution": recommendation
    }

from investor.models import InvestmentOffer, Negotiation
from collections import Counter

def calculate_investor_interest(project_id):
    offers = InvestmentOffer.objects.filter(project_id=project_id)
    negotiations = Negotiation.objects.filter(offer__project_id=project_id)

    total_offers = offers.count()
    total_negotiations = negotiations.count()
    accepted_offers = offers.filter(status='accepted').count()
    rejected_offers = offers.filter(status='rejected').count()

    # Count of unique investors interested
    unique_investors = offers.values_list('investor_id', flat=True).distinct().count()

    if total_offers == 0:
        interest_level = "❌ No investment offers yet. Try improving the project's visibility and marketing to investors."
    elif total_offers >= 5 and total_negotiations >= 5:
        interest_level = "🔥 High investor interest. Offers and negotiations are increasing."
    elif total_offers >= 2:
        interest_level = "📈 Good interest from some investors."
    else:
        interest_level = "🔍 Investor interest is still low. Consider enhancing the project’s pitch."

    return {
        "total_offers": total_offers,
        "accepted_offers": accepted_offers,
        "rejected_offers": rejected_offers,
        "total_negotiations": total_negotiations,
        "unique_investors": unique_investors,
        "interest_level": interest_level,
    }


from .models import FeasibilityStudy

import re
from .models import FeasibilityStudy

import re

import re

def analyze_capital_recovery(project_id):
    try:
        fs = FeasibilityStudy.objects.get(project_id=project_id)
    except FeasibilityStudy.DoesNotExist:
        return {"error": "No feasibility study found for this project."}

    # Extract expected monthly revenue from text (e.g., "9,000 - 12,000 USD")
    try:
        revenue_str = fs.expected_monthly_revenue
        if not revenue_str:
            raise ValueError("Monthly revenue not available")

        # Extract numbers
        matches = re.findall(r"[\d,]+", revenue_str)
        numbers = [float(val.replace(',', '')) for val in matches]

        if not numbers:
            revenue = 0
        elif len(numbers) == 1:
            revenue = numbers[0]
        else:
            revenue = sum(numbers) / len(numbers)  # Average of the two bounds

    except Exception:
        revenue = 0

    try:
        funding = float(fs.funding_required)
    except:
        funding = 0

    # Calculate actual ROI period
    if revenue > 0:
        roi_months = round(funding / revenue, 2)
    else:
        roi_months = None

    # Generate message based on calculated period
    if revenue == 0 or funding == 0:
        message = "⚠️ Unable to evaluate capital recovery due to missing data."
    elif roi_months <= 6:
        message = "✅ The project is expected to recover capital quickly within 6 months – Excellent!"
    elif 6 < roi_months <= 12:
        message = "🟡 Capital recovery within a year – Acceptable, but consider improving revenue or reducing costs."
    elif 12 < roi_months <= 24:
        message = "⚠️ Recovery period is longer than a year – Re-evaluate the business plan and feasibility."
    else:
        message = "❌ Capital recovery takes more than two years – The project is currently high risk."

    return {
        "expected_monthly_revenue": revenue,
        "funding_required": funding,
        "calculated_roi_months": roi_months,
        "capital_recovery_health": message
    }


# services/value_analysis.py



# your_app/data_analysis.py
from .models import FeasibilityStudy
from projectOwner.models import Project

def parse_expected_revenue(revenue_str):
    """
    يحاول استخراج متوسط الإيرادات الشهرية من نص يمكن أن يكون نطاق مثل "9,000 - 12,000 USD"
    """
    if not revenue_str:
        return 0
    try:
        # إزالة "USD" والفواصل
        clean_str = revenue_str.replace("USD", "").replace(",", "").strip()
        # إذا فيه "-"، يعني نطاق
        if "-" in clean_str:
            parts = clean_str.split("-")
            nums = []
            for part in parts:
                num = float(part.strip())
                nums.append(num)
            return sum(nums) / len(nums)  # المتوسط
        else:
            return float(clean_str)
    except:
        return 0

def get_strengths_and_weaknesses(project_id):
    try:
        fs = FeasibilityStudy.objects.get(project_id=project_id)
    except FeasibilityStudy.DoesNotExist:
        return {"error": "لا يوجد دراسة جدوى لهذا المشروع."}

    strengths = []
    weaknesses = []

    # الإيرادات الشهرية المتوقعة
    expected_revenue = parse_expected_revenue(fs.expected_monthly_revenue)
    if expected_revenue >= 10000:
        strengths.append("إيرادات شهرية متوقعة عالية")
    elif expected_revenue < 3000 and expected_revenue > 0:
        weaknesses.append("الإيرادات الشهرية المتوقعة منخفضة")
    else:
        weaknesses.append("لا توجد بيانات واضحة عن الإيرادات الشهرية المتوقعة")

    # هامش الربح المتوقع
    try:
        profit_margin = float(fs.expected_profit_margin.replace("%", "").strip())
        if profit_margin >= 20:
            strengths.append("هامش ربح مرتفع")
        elif profit_margin < 10:
            weaknesses.append("هامش الربح منخفض")
    except:
        weaknesses.append("لا توجد بيانات واضحة عن هامش الربح")

    # الاستثمار في الفريق والتسويق
    total_investment = fs.team_investment_percentage + fs.marketing_investment_percentage
    if total_investment >= 50:
        strengths.append("استثمار جيد في الفريق والتسويق")
    else:
        weaknesses.append("الاستثمار في الفريق والتسويق ضعيف")

    # فرصة النمو
    if fs.growth_opportunity and len(fs.growth_opportunity.strip()) > 30:
        strengths.append("فرصة نمو واضحة")
    else:
        weaknesses.append("فرصة النمو غير واضحة")

    # فترة استرداد رأس المال
    if fs.roi_period_months <= 12:
        strengths.append("فترة استرداد رأس المال قصيرة")
    elif fs.roi_period_months > 18:
        weaknesses.append("فترة استرداد رأس المال طويلة")

    # نسبة التمويل إلى الإيرادات الحالية
    try:
        funding = float(fs.funding_required)
        current_rev = float(fs.current_revenue or 0)
        if current_rev > 0:
            if funding <= 2 * current_rev:
                strengths.append("التمويل المطلوب مناسب للإيرادات الحالية")
            else:
                weaknesses.append("التمويل المطلوب أعلى بكثير من الإيرادات الحالية")
        else:
            weaknesses.append("لا توجد إيرادات حالية لتقييم التمويل")
    except (ValueError, TypeError):
        weaknesses.append("خطأ في بيانات التمويل أو الإيرادات")

    return {
        "strengths": strengths,
        "weaknesses": weaknesses,
    }


from .models import FeasibilityStudy, Project

def analyze_readiness_alignment(project_id):
    try:
        project = Project.objects.get(id=project_id)
        fs = project.feasibility_study
    except Project.DoesNotExist:
        return {"error": "Project not found."}
    except FeasibilityStudy.DoesNotExist:
        return {"error": "No feasibility study available for this project."}

    readiness = project.readiness_level
    expected_revenue = 0

    try:
        if fs.expected_monthly_revenue:
            def parse_expected_revenue(revenue_str):
                if not revenue_str:
                    return 0
                try:
                    clean_str = revenue_str.replace("USD", "").replace(",", "").strip()
                    if "-" in clean_str:
                        parts = clean_str.split("-")
                        nums = [float(part.strip()) for part in parts]
                        return sum(nums) / len(nums)
                    else:
                        return float(clean_str)
                except:
                    return 0
            expected_revenue = parse_expected_revenue(fs.expected_monthly_revenue)
    except:
        expected_revenue = 0

    analysis = ""
    score = 0

    if readiness == "idea":
        analysis = "🚧 The project is at the idea stage. It needs clear development and a prototype before market entry."
        score = 30
        if expected_revenue > 5000:
            analysis += " However, there are promising revenue expectations that should be leveraged with a clear plan."
            score += 10

    elif readiness == "prototype":
        analysis = "🧪 The project is at the prototype stage. It's suitable for market testing and iteration based on feedback."
        score = 60
        if expected_revenue > 8000:
            analysis += " Strong revenue expectations indicate good potential for success."
            score += 15

    elif readiness == "existing":
        analysis = "✅ The project is already operational and market-ready. Focus should be on scaling and growth."
        score = 90

        funding = float(fs.funding_required or 0)
        team_marketing_investment = fs.team_investment_percentage + fs.marketing_investment_percentage

        if expected_revenue < 3000:
            if funding > 10000 and team_marketing_investment < 40:
                analysis += " Revenue is low compared to funding and investment size. Consider reviewing the growth and marketing strategy."
                score -= 25
            elif funding <= 10000 or team_marketing_investment >= 40:
                analysis += " Revenue is low, but investment in team and marketing is good. Performance can be improved without major concern."
                score -= 10
        elif expected_revenue >= 3000:
            analysis += " Revenue is reasonable for the size of the project."

    else:
        analysis = "❓ Project readiness level is not clearly defined."
        score = 0

    score = max(0, min(100, score))

    return {
        "readiness_level": readiness,
        "readiness_score": score,
        "analysis": analysis
    }


from .models import FeasibilityStudy, Project

def cost_to_revenue_analysis(feasibility_study):
    """
    Comprehensive analysis of funding versus revenue, considering various factors.
    If the project is still at the idea or prototype stage, financial analysis is skipped.
    """

    def parse_expected_revenue(revenue_str):
        if not revenue_str:
            return 0.0
        try:
            clean_str = revenue_str.replace("USD", "").replace(",", "").strip()
            if "-" in clean_str:
                parts = clean_str.split("-")
                nums = [float(p.strip()) for p in parts if p.strip().replace('.', '', 1).isdigit()]
                return sum(nums) / len(nums) if nums else 0.0
            else:
                return float(clean_str)
        except Exception:
            return 0.0

    def parse_profit_margin(profit_margin_str):
        if not profit_margin_str:
            return 0.0
        try:
            return float(profit_margin_str.replace("%", "").strip()) / 100
        except Exception:
            return 0.0

    # Extract readiness level
    readiness = getattr(feasibility_study.project, "readiness_level", None)

    # ✅ Skip financial analysis if the project is in the "idea" or "prototype" stage
    if readiness in ['idea', 'prototype']:
        return {
            "funding_required": float(feasibility_study.funding_required or 0),
            "expected_annual_profit": 0,
            "roi_period_months": feasibility_study.roi_period_months or 0,
            "capital_recovery_speed_years": None,
            "is_profitable": False,
            "analysis_messages": [
                "🚧 Project is still in the idea or prototype stage. Financial analysis is not applicable at this point."
            ],
            "recommendations": [
                "Start developing a simple MVP to test core functionality.",
                "Test market demand through low-cost methods.",
                "Build a basic financial plan before seeking large funding.",
                "Focus on validating core assumptions before scaling."
            ]
        }

    # Proceed with financial analysis
    funding_required = float(feasibility_study.funding_required or 0)
    expected_monthly_revenue = parse_expected_revenue(feasibility_study.expected_monthly_revenue)
    profit_margin = parse_profit_margin(feasibility_study.expected_profit_margin)
    roi_period = feasibility_study.roi_period_months or 0
    roi_period_years = roi_period / 12 if roi_period > 0 else float('inf')
    marketing_pct = feasibility_study.marketing_investment_percentage or 0
    team_pct = feasibility_study.team_investment_percentage or 0
    market_potential = feasibility_study.market_potential or 0
    risk_assessment = feasibility_study.risk_assessment or 0
    competitive_edge = feasibility_study.competitive_edge or 0

    # Calculate expected annual profit
    expected_annual_profit = expected_monthly_revenue * 12 * profit_margin

    # Calculate capital recovery period
    capital_recovery_speed = (funding_required / expected_annual_profit) if expected_annual_profit > 0 else float('inf')
    is_profitable = expected_annual_profit >= funding_required

    analysis_messages = []
    recommendations = []

    if is_profitable:
        analysis_messages.append("✅ Expected annual profit exceeds required funding.")
    else:
        analysis_messages.append("❌ Required funding is higher than the expected annual profit.")

    if capital_recovery_speed <= roi_period_years and capital_recovery_speed != float('inf'):
        analysis_messages.append(
            f"⏳ ROI period ({roi_period} months) aligns with recovery speed ({capital_recovery_speed:.2f} years)."
        )
    else:
        analysis_messages.append(
            f"⚠️ ROI period ({roi_period} months) is longer than expected based on current profitability ({capital_recovery_speed:.2f} years)."
        )
        recommendations.append("Review business model to reduce capital recovery time.")

    if (marketing_pct + team_pct) < 50:
        recommendations.append("Consider increasing investment in the team and marketing to improve success potential.")

    if market_potential < 0.5:
        recommendations.append("Market potential is limited. Consider expanding your target market.")
    if risk_assessment > 0.7:
        recommendations.append("Risk level is high. Develop a risk mitigation plan.")
    if competitive_edge < 0.4:
        recommendations.append("Weak competitive edge. Focus on enhancing unique value propositions.")

    if not is_profitable:
        recommendations.append("Consider revisiting pricing, increasing revenue, or reducing costs to improve profitability.")

    return {
        "funding_required": funding_required,
        "expected_annual_profit": expected_annual_profit,
        "roi_period_months": roi_period,
        "capital_recovery_speed_years": capital_recovery_speed,
        "is_profitable": is_profitable,
        "analysis_messages": analysis_messages,
        "recommendations": recommendations,
    }
