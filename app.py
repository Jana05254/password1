from flask import Flask, render_template, request
import string
import random
import secrets  # استخدام مكتبة secrets لتوليد كلمات مرور أقوى

app = Flask(__name__)

# --- كلمات مرور شائعة للتحقق (مبسط) ---
common_passwords = ["123456", "password", "qwerty", "admin", "user"]

# --- دالة بسيطة لتقييم قوة كلمة المرور بناءً على الميزات ---
def analyze_password_strength_manual(password):
    score = 0
    if len(password) >= 12:
        score += 1
    if any(c.islower() for c in password):
        score += 1
    if any(c.isupper() for c in password):
        score += 1
    if any(c.isdigit() for c in password):
        score += 1
    if any(c in string.punctuation for c in password):
        score += 1
    if len(set(password)) >= 8:
        score += 1
    return score / 6  # تقييم على مقياس من 0 إلى 1

def analyze_password_strength(password):
    manual_strength = analyze_password_strength_manual(password)

    if manual_strength >= 0.75:
        return "قوية", "Strong", "green"
    elif manual_strength >= 0.5:
        return "متوسطة", "Medium", "orange"
    else:
        return "ضعيفة", "Weak", "red"

def is_common_password(password):
    return password in common_passwords

def estimate_brute_force_time(password):
    characters = string.ascii_lowercase + string.ascii_uppercase + string.digits + string.punctuation
    num_possible_chars = len(characters)

    if len(password) == 0:
        return "فوري", "Instant"

    num_possible_combinations = num_possible_chars ** len(password)
    attempts_per_second = 10**9
    time_in_seconds = num_possible_combinations / attempts_per_second

    if time_in_seconds < 1:
        return "أقل من ثانية", "Less than a second"
    elif time_in_seconds < 60:
        return f"{time_in_seconds:.2f} ثانية", f"{time_in_seconds:.2f} seconds"
    elif time_in_seconds < 3600:
        minutes = int(time_in_seconds // 60)
        seconds = int(time_in_seconds % 60)
        return f"{minutes} دقيقة و {seconds} ثانية", f"{minutes} minutes and {seconds} seconds"
    elif time_in_seconds < 86400:
        hours = int(time_in_seconds // 3600)
        minutes = int((time_in_seconds % 3600) // 60)
        return f"{hours} ساعة و {minutes} دقيقة", f"{hours} hours and {minutes} minutes"
    elif time_in_seconds < 31536000:
        days = int(time_in_seconds // 86400)
        hours = int((time_in_seconds % 86400) // 3600)
        return f"{days} يومًا و {hours} ساعة", f"{days} days and {hours} hours"
    elif time_in_seconds < 31536000 * 100:
        years = time_in_seconds // 31536000
        months = int((time_in_seconds % 31536000) // (31536000 / 12))
        return f"{int(years)} سنة و {months} شهرًا", f"{int(years)} years and {months} months"
    else:
        years = time_in_seconds // 31536000
        return f"{int(years)} سنة أو أكثر", f"{int(years)} years or more"

def generate_suggested_password(length=16): # زيادة طول كلمة المرور المقترحة
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(characters) for i in range(length)), ''.join(secrets.choice(characters) for i in range(length))

@app.route('/', methods=['GET', 'POST'])
def index():
    results = None
    suggestions = None
    attacks_info = None

    if request.method == 'POST':
        password = request.form['password']
        strength_ar, strength_en, color = analyze_password_strength(password)
        is_common = is_common_password(password)
        time_to_crack_ar, time_to_crack_en = estimate_brute_force_time(password)

        results = {
            'strength_ar': strength_ar,
            'strength_en': strength_en,
            'color': color,
            'is_common': is_common,
            'time_to_crack_ar': time_to_crack_ar,
            'time_to_crack_en': time_to_crack_en
        }

        if strength_en == "Weak":
            suggested_password_ar, suggested_password_en = generate_suggested_password(password)
            suggestions = {
                'suggested_ar': suggested_password_ar,
                'suggested_en': suggested_password_en,
                'improve_ar': [],
                'improve_en': []
            }
            if len(password) < 12:
                suggestions['improve_ar'].append("زيادة طول كلمة المرور (استهدف 12 حرفًا على الأقل).")
                suggestions['improve_en'].append("Increase the length of your password (aim for at least 12 characters).")
            if not any(c.islower() for c in password):
                suggestions['improve_ar'].append("تضمين أحرف صغيرة.")
                suggestions['improve_en'].append("Include lowercase letters.")
            if not any(c.isupper() for c in password):
                suggestions['improve_ar'].append("تضمين أحرف كبيرة.")
                suggestions['improve_en'].append("Include uppercase letters.")
            if not any(c.isdigit() for c in password):
                suggestions['improve_ar'].append("تضمين أرقام.")
                suggestions['improve_en'].append("Include numbers.")
            if not any(c in string.punctuation for c in password):
                suggestions['improve_ar'].append("تضمين رموز (مثل !@#$%^&*).")
                suggestions['improve_en'].append("Include symbols (e.g., !@#$%^&*).")
            suggestions['improve_ar'].append("تجنب استخدام المعلومات الشخصية أو الكلمات الشائعة.")
            suggestions['improve_en'].append("Avoid using personal information or common words.")
        else:
            suggestions = None

        attacks_info = {
            'title_ar': 'معلومات حول الهجمات المحتملة',
            'title_en': 'Potential Attack Information',
            'brute_force_ar': 'هجوم القوة الغاشمة',
            'brute_force_en': 'Brute-Force Attack',
            'brute_force_desc_ar': 'يحاول تخمين جميع الاحتمالات الممكنة.',
            'brute_force_desc_en': 'Attempts to guess all possible combinations.',
            'dictionary_ar': 'هجوم القاموس',
            'dictionary_en': 'Dictionary Attack',
            'dictionary_desc_ar': 'يستخدم قائمة بكلمات شائعة لتخمين كلمة المرور.',
            'dictionary_desc_en': 'Uses a list of common words to guess the password.',
            'phishing_ar': 'هجمات التصيد الاحتيالي',
            'phishing_en': 'Phishing Attacks',
            'phishing_desc_ar': 'محاولات لخداعك للكشف عن كلمة مرورك.',
            'phishing_desc_en': 'Attempts to trick you into revealing your password.',
            'pattern_ar': 'هجمات تخمين الأنماط',
            'pattern_en': 'Pattern Guessing Attacks',
            'pattern_desc_ar': 'استغلال الأنماط الشائعة في كلمات المرور.',
            'pattern_desc_en': 'Exploiting common patterns in passwords.'
        }

    return render_template('index.html', results=results, suggestions=suggestions, attacks_info=attacks_info)

if __name__ == '__main__':
    app.run(debug=True)