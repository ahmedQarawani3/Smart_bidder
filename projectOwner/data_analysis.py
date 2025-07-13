# data_analysis.py

from decimal import Decimal, InvalidOperation
from .models import FeasibilityStudy
from investor.models import InvestmentOffer, Negotiation

def calculate_detailed_project_analysis(project_id):
    try:
        fs = FeasibilityStudy.objects.get(project_id=project_id)
    except FeasibilityStudy.DoesNotExist:
        return {"error": "No feasibility study found for this project."}

    # تحديد مرحلة الجاهزية
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

    # ===== حفظ النتائج في قاعدة البيانات =====
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



# projectOwner/analysis_tools/project_analysis.py

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
            "investment_distribution": "⚠️ لا يوجد توزيع استثماري محدد للفريق أو التسويق."
        }

    diff = abs(team - marketing)

    if diff <= 10:
        recommendation = "✅ توزيع الاستثمار بين الفريق والتسويق متوازن، هذا أمر جيد."
    elif team > marketing:
        recommendation = "👥 الاستثمار أكبر في الفريق. فكر في تعزيز استثمار التسويق لزيادة الوصول إلى السوق."
    else:
        recommendation = "📢 الاستثمار أكبر في التسويق. تأكد من أن الفريق لديه القدرة على تلبية النمو المتوقع."

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

    # عدد المستثمرين الفريدين المهتمين
    unique_investors = offers.values_list('investor_id', flat=True).distinct().count()

    if total_offers == 0:
        interest_level = "❌ لا يوجد عروض استثمارية بعد. حاول تعزيز وضوح المشروع وتسويقه للمستثمرين."
    elif total_offers >= 5 and total_negotiations >= 5:
        interest_level = "🔥 اهتمام مرتفع من المستثمرين، العروض والمفاوضات في تزايد."
    elif total_offers >= 2:
        interest_level = "📈 هنالك اهتمام جيد من بعض المستثمرين."
    else:
        interest_level = "🔍 الاهتمام لا يزال منخفضًا. حاول تحسين العرض التقديمي للمشروع."

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

def analyze_capital_recovery(project_id):
    try:
        fs = FeasibilityStudy.objects.get(project_id=project_id)
    except FeasibilityStudy.DoesNotExist:
        return {"error": "No feasibility study found for this project."}

    # استخراج رقم تقريبي من expected_monthly_revenue
    try:
        revenue_str = fs.expected_monthly_revenue
        if not revenue_str:
            raise ValueError("No revenue string provided")

        # إذا كان مثل: "9,000 - 12,000 USD"
        matches = re.findall(r"[\d,]+", revenue_str)
        numbers = [float(val.replace(',', '')) for val in matches]

        if len(numbers) == 0:
            revenue = 0
        elif len(numbers) == 1:
            revenue = numbers[0]
        else:
            revenue = sum(numbers) / len(numbers)  # متوسط بين الحد الأدنى والأعلى

    except Exception:
        revenue = 0

    roi_months = fs.roi_period_months
    funding = float(fs.funding_required)

    if revenue == 0:
        message = "⚠️ لا يمكن تقييم استرداد رأس المال بسبب عدم توفر الإيرادات المتوقعة."
    elif roi_months <= 6:
        message = "✅ المشروع يُتوقع أن يسترد رأس المال بسرعة خلال 6 أشهر – ممتاز!"
    elif 6 < roi_months <= 12:
        message = "🟡 استرداد رأس المال خلال سنة – مقبول ولكن يفضل تحسين الأرباح أو تقليل التكاليف."
    elif 12 < roi_months <= 24:
        message = "⚠️ فترة الاسترداد أطول من سنة – راجع خطة العمل وقيّم الجدوى."
    else:
        message = "❌ استرداد رأس المال يتطلب أكثر من سنتين – المشروع عالي المخاطرة حاليًا."

    return {
        "roi_period_months": roi_months,
        "expected_monthly_revenue": revenue,
        "funding_required": funding,
        "capital_recovery_health": message
    }
# services/value_analysis.py
import re
from .models import FeasibilityStudy

# value_for_investment_analysis.py
from .models import FeasibilityStudy

def analyze_value_for_investment(project_id):
    try:
        fs = FeasibilityStudy.objects.get(project_id=project_id)
    except FeasibilityStudy.DoesNotExist:
        return {"value_for_investment": "❌ لا يوجد دراسة جدوى لهذا المشروع."}

    try:
        # تحويل الإيراد المتوقع وهامش الربح إلى أرقام
        expected_revenue = float(fs.expected_monthly_revenue.replace(",", "").split()[0])
        profit_margin = float(fs.expected_profit_margin.replace("%", "").strip())
        funding_required = float(fs.funding_required)
    except:
        return {"value_for_investment": "⚠️ لا يمكن حساب العائد بسبب مشاكل في البيانات المدخلة."}

    if expected_revenue <= 0 or profit_margin <= 0 or funding_required <= 0:
        return {"value_for_investment": "⚠️ البيانات غير كافية لحساب القيمة مقابل الاستثمار."}

    # ✅ حساب الربح السنوي الصافي
    net_annual_profit = expected_revenue * 12 * (profit_margin / 100)

    # ✅ حساب ROI السنوي
    roi_score = (net_annual_profit / funding_required) * 100

    # ✅ تقييم
    if roi_score > 100:
        message = f"✅ المشروع يقدم قيمة عالية مقابل الاستثمار – ROI = {roi_score:.2f}٪."
    elif roi_score > 50:
        message = f"📈 المشروع يقدم قيمة جيدة – ROI = {roi_score:.2f}٪."
    elif roi_score > 20:
        message = f"⚠️ المشروع متوسط القيمة – ROI = {roi_score:.2f}٪. ينصح بمراجعة التكاليف أو تحسين الربحية."
    else:
        message = f"❌ المشروع لا يقدم قيمة جيدة حاليًا مقابل التمويل – ROI = {roi_score:.2f}٪."

    return {"value_for_investment": message}

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
        return {"error": "المشروع غير موجود."}
    except FeasibilityStudy.DoesNotExist:
        return {"error": "لا يوجد دراسة جدوى لهذا المشروع."}

    readiness = project.readiness_level
    expected_revenue = 0
    try:
        if fs.expected_monthly_revenue:
            # نفس دالة التحويل للنصوص بنطاق الإيرادات لو موجودة
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
        analysis = "🚧 المشروع في مرحلة الفكرة، يحتاج إلى تطوير واضح ونموذج تجريبي قبل دخول السوق."
        score = 30
        if expected_revenue > 5000:
            analysis += " رغم ذلك، هناك توقعات جيدة للإيرادات يجب استغلالها مع بناء خطة واضحة."
            score += 10

    elif readiness == "prototype":
        analysis = "🧪 المشروع في مرحلة النموذج الأولي، مناسب لاختبار السوق والتعديل بناءً على ردود الفعل."
        score = 60
        if expected_revenue > 8000:
            analysis += " توقعات الإيرادات قوية وهذا مؤشر جيد لنجاح المشروع."
            score += 15

    elif readiness == "existing":
        analysis = "✅ المشروع قائم وجاهز للسوق، يجب التركيز على تسريع النمو والتوسع."
        score = 90
        if expected_revenue < 3000:
            analysis += " بالرغم من جاهزية المشروع، الإيرادات المتوقعة منخفضة وينبغي تحسين الاستراتيجية التسويقية."
            score -= 20
    else:
        analysis = "❓ مستوى جاهزية المشروع غير محدد بشكل صحيح."
        score = 0

    # ضبط score بين 0 و 100
    score = max(0, min(100, score))

    return {
        "readiness_level": readiness,
        "readiness_score": score,
        "analysis": analysis
    }
from .models import FeasibilityStudy, Project

def generate_improvement_suggestions(project_id):
    try:
        fs = FeasibilityStudy.objects.get(project_id=project_id)
        project = fs.project
    except FeasibilityStudy.DoesNotExist:
        return {"error": "لا يوجد دراسة جدوى لهذا المشروع."}
    except Project.DoesNotExist:
        return {"error": "المشروع غير موجود."}

    suggestions = []

    # تحسين الإيرادات المتوقعة
    try:
        expected_revenue = 0
        if fs.expected_monthly_revenue:
            clean_str = fs.expected_monthly_revenue.replace("USD", "").replace(",", "").strip()
            if "-" in clean_str:
                parts = clean_str.split("-")
                nums = [float(p.strip()) for p in parts]
                expected_revenue = sum(nums) / len(nums)
            else:
                expected_revenue = float(clean_str)
        if expected_revenue < 5000:
            suggestions.append("ضع خطة تسويقية أفضل لزيادة الإيرادات الشهرية المتوقعة.")
    except:
        suggestions.append("تحديث بيانات الإيرادات الشهرية المتوقعة لتحسين التحليل.")

    # هامش الربح
    try:
        profit_margin = float(fs.expected_profit_margin.replace("%", "").strip())
        if profit_margin < 15:
            suggestions.append("راجع هيكل التكاليف لزيادة هامش الربح المتوقع.")
    except:
        suggestions.append("تحديث بيانات هامش الربح المتوقع ضروري لتحليل أفضل.")

    # فترة استرداد رأس المال
    if fs.roi_period_months > 18:
        suggestions.append("حاول تحسين نموذج العمل لتقليل فترة استرداد رأس المال.")

    # استثمار الفريق والتسويق
    total_investment = fs.team_investment_percentage + fs.marketing_investment_percentage
    if total_investment < 50:
        suggestions.append("قم بزيادة الاستثمار في الفريق والتسويق لتعزيز فرص النجاح.")

    # فرصة النمو
    if not fs.growth_opportunity or len(fs.growth_opportunity.strip()) < 30:
        suggestions.append("وضح فرص النمو المحتملة بشكل أفضل لجذب المستثمرين.")

    # حالة المشروع
    if project.status == 'under_negotiation':
        suggestions.append("ركز على تحسين العروض والتفاوض لزيادة فرص التمويل.")
    elif project.status == 'closed':
        suggestions.append("راجع أسباب إغلاق المشروع لتجنبها في المستقبل.")

    return {
        "improvement_suggestions": suggestions if suggestions else ["لا توجد اقتراحات لتحسين المشروع حالياً."]
    }
