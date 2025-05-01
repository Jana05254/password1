import ipywidgets as widgets
from IPython.display import display, HTML
import string
import random
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Dropout

# --- كلمات مرور شائعة للتحقق (مبسط) ---
common_passwords = ["123456", "password", "qwerty", "admin", "user"]

# --- تجهيز نموذج مبسط للتحليل ---
passwords = ["123456", "password", "qwerty", "abc123", "Password1!",
             "StrongPass123!", "P@ssw0rd!", "admin1234", "helloWorld2025",
             "mycat2023", "summerFun!", "codingIsCool", "secretKey-1", "applePie1"]

def encode_passwords(passwords):
    chars = string.ascii_letters + string.digits + string.punctuation
    char_to_int = {ch: i for i, ch in enumerate(chars)}
    int_passwords = []
    for password in passwords:
        int_passwords.append([char_to_int[char] for char in password if char in char_to_int])
    return int_passwords, char_to_int, len(chars)

int_passwords, char_to_int, n_chars = encode_passwords(passwords)
max_length = max([len(pwd) for pwd in int_passwords])

X = np.zeros((len(int_passwords), max_length, n_chars))
y = np.zeros((len(int_passwords), 1))

for i, pwd in enumerate(int_passwords):
    for j, char in enumerate(pwd):
        X[i, j, char] = 1
    y[i] = 1 if len(pwd) >= 10 else 0

model = Sequential()
model.add(LSTM(64, input_shape=(max_length, n_chars), return_sequences=True))
model.add(Dropout(0.3))
model.add(LSTM(64))
model.add(Dropout(0.3))
model.add(Dense(32, activation='relu'))
model.add(Dense(1, activation='sigmoid'))
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
model.fit(X, y, epochs=50, batch_size=1, verbose=0)

def analyze_password_strength_model(password):
    features = np.zeros((1, len(password), n_chars))
    for i, char in enumerate(password):
        if char in char_to_int:
            features[0, i, char_to_int[char]] = 1
    strength_model = model.predict(features, verbose=0)[0][0]
    return strength_model

def analyze_password_strength_manual(password):
    score = 0
    if len(password) >= 8:
        score += 1
    has_lower = any(c.islower() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_symbol = any(c in string.punctuation for c in password)

    if has_lower:
        score += 1
    if has_upper:
        score += 1
    if has_digit:
        score += 1
    if has_symbol:
        score += 1

    return score / 5

def analyze_password_strength(password):
    strength_model = analyze_password_strength_model(password)
    manual_strength = analyze_password_strength_manual(password)
    final_score = (strength_model + manual_strength) / 2

    if final_score >= 0.8:
        return "جيدة", "Good", "#4CAF50"
    elif final_score >= 0.5:
        return "مقبولة", "Acceptable", "#FFC107"
    else:
        return "ضعيفة", "Weak", "#F44336"

def get_strength_feedback(password):
    feedback = []
    if len(password) < 8:
        feedback.append("يفضل أن تكون كلمة المرور أطول من 8 أحرف.")
    if not any(c.islower() for c in password):
        feedback.append("يفضل تضمين أحرف صغيرة.")
    if not any(c.isupper() for c in password):
        feedback.append("يفضل تضمين أحرف كبيرة.")
    if not any(c.isdigit() for c in password):
        feedback.append("يفضل تضمين أرقام.")
    if not any(c in "!@#$%^&*" for c in password):
        feedback.append("يفضل تضمين رموز (مثل ! @ # $ % ^ & *).")
    return "<br>".join(feedback)

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

def generate_suggested_password(weak_password):
    if not weak_password:
        return "جرب كلمة مرور أطول", "Try a longer password"

    suggestion = list(weak_password)
    length_needed = max(0, 12 - len(suggestion))
    added_chars = ""
    possible_chars = ""

    if not any(c.isupper() for c in suggestion):
        possible_chars += string.ascii_uppercase
    if not any(c.isdigit() for c in suggestion):
        possible_chars += string.digits
    if not any(c in "!@#$%^&*" for c in suggestion):
        possible_chars += "!@#$%^&*"
    possible_chars += string.ascii_lowercase + string.digits # إضافة حروف صغيرة وأرقام دائمًا

    if possible_chars:
        added_chars += ''.join(random.choice(possible_chars) for _ in range(length_needed))

    suggestion.extend(list(added_chars))
    random.shuffle(suggestion)
    return "".join(suggestion), "".join(suggestion)

def generate_realistic_password(length=10):
    vowels = "aeiou"
    consonants = "".join(c for c in string.ascii_lowercase if c not in vowels)
    password = ""
    for i in range(length):
        if i % 2 == 0:
            password += random.choice(consonants)
        else:
            password += random.choice(vowels)
    password_list = list(password)
    # إضافة بعض التعقيد بشكل عشوائي
    for _ in range(random.randint(1, 3)):
        index_to_change = random.randint(0, length - 1)
        if random.random() < 0.3:
            password_list[index_to_change] = random.choice(string.digits)
        elif random.random() < 0.3:
            password_list[index_to_change] = random.choice(string.ascii_uppercase)
        else:
            password_list[index_to_change] = random.choice("!@#$%^&*")
    return "".join(password_list)

# واجهة المستخدم باستخدام ipywidgets مع تصميم مبسط وتوضيح لسبب ضعف كلمة المرور
password_input = widgets.Password(
    description="أدخل كلمة المرور:",
    placeholder="كلمة المرور هنا",
    style={'description_width': 'initial'},
    layout=widgets.Layout(width='50%')
)

analyze_button = widgets.Button(
    description="تحليل",
    button_style='info',
    style={'font_weight': 'bold', 'button_color': '#2196F3', 'text_color': 'white'},
    layout=widgets.Layout(width='20%', margin='10px 0')
)

results_output = widgets.HTML(value="", layout=widgets.Layout(margin='10px 0', padding='10px', border_radius='5px'))
suggestions_output = widgets.HTML(value="", layout=widgets.Layout(margin='10px 0', padding='10px', border_radius='5px'))
attacks_info_output = widgets.HTML(value="", layout=widgets.Layout(margin='10px 0', padding='10px', border_radius='5px', background_color='#f0f8ff', style={'color': 'red'}))
strength_feedback_output = widgets.HTML(value="", layout=widgets.Layout(margin='10px 0', padding='10px', border_radius='5px', color='#d32f2f'))

strong_password_message = widgets.HTML(value="", layout=widgets.Layout(margin='10px 0', padding='10px', border_radius='5px'))

def on_analyze_button_clicked(b):
    password = password_input.value
    strength_ar, strength_en, color = analyze_password_strength(password)
    is_common = is_common_password(password)
    time_to_crack_ar, time_to_crack_en = estimate_brute_force_time(password)
    suggested_password_ar, suggested_password_en = ("", "")
    strong_message_html = ""
    feedback_html = ""
    additional_suggestions_ar = ""
    additional_suggestions_en = ""

    if strength_en == "Weak" or strength_en == "Acceptable":
        suggested_password_ar, suggested_password_en = generate_suggested_password(password)
        suggested_password_html = f"""
            <p>🔑 <strong>اقتراح لكلمة مرور جديدة (معدلة):</strong><br>
            <span style='font-size: 1.2em; color: #007bff;'>{suggested_password_ar}</span>
            <button style='padding: 5px 10px; font-size: 0.9em; margin-right: 5px;' onclick="navigator.clipboard.writeText('{suggested_password_ar}')">نسخ</button><br>
            ({suggested_password_en})</p>
        """
        feedback_html = f"<p><strong>نصائح لتحسين كلمة المرور:</strong></p><p>{get_strength_feedback(password)}</p>"

        additional_suggestions_ar = "<p><strong>اقتراحات إضافية لكلمات المرور:</strong></p><ul>"
        additional_suggestions_en = "<p><strong>Additional password suggestions:</strong></p><ul>"
        for _ in range(3): # توليد 3 كلمات مرور أكثر منطقية
            realistic_password = generate_realistic_password(random.randint(8, 12))
            additional_suggestions_ar += f"<li>{realistic_password}</li>"
            additional_suggestions_en += f"<li>{realistic_password}</li>"
        additional_suggestions_ar += "</ul>"
        additional_suggestions_en += "</ul>"
        suggestions_output.value = f'<div style="">{additional_suggestions_ar}<br>{additional_suggestions_en}</div>'
    else:
        suggested_password_html = ""
        feedback_html = ""
        suggestions_output.value = ""

    strength_feedback_output.value = feedback_html


    if strength_en == "Good":
        strong_message_html = f"<div style='background-color: #e6ffe6; border: 1px solid #ccffcc; color: #4CAF50; font-weight: bold;'>تهانينا! كلمة مرور جيدة.</div>"
        strong_password_message.value = strong_message_html
    else:
        strong_password_message.value = ""

    results_html = f"""
        <div style='font-size: 1.1em;'>
            <p><strong>قوة كلمة المرور:</strong> <span style='color: {color}; font-weight: bold;'>{strength_ar}</span> ({strength_en})</p>
            <p><strong>الوقت المقدر للاختراق:</strong> <span style='font-weight: bold;'>{time_to_crack_ar}</span> ({time_to_crack_en})</p>
            <p style='color:#f44336; font-weight:bold;'>{'تحذير: كلمة مرور شائعة!' if is_common else ''}</p>
            {strong_password_message}
            {suggested_password_html}
        </div>
    """
    results_output.value = results_html


    attacks_info = f"""
        <div style='padding: 10px; border: 1px solid #eee; background-color: #f0f8ff; border-radius: 5px; color: red;'>
            <b>معلومات حول الهجمات المحتملة (Potential Attack Information):</b><br>
            - <b>هجوم القوة الغاشمة (Brute-Force Attack):</b> يحاول تخمين جميع الاحتمالات الممكنة.<br>
            - <b>هجوم القاموس (Dictionary Attack):</b> يستخدم قائمة بكلمات شائعة لتخمين كلمة المرور.<br>
            - <b>هجمات التصيد الاحتيالي (Phishing Attacks):</b> محاولات لخداعك للكشف عن كلمة مرورك.<br>
            - <b>هجمات تخمين الأنماط (Pattern Guessing Attacks):</b> استغلال الأنماط الشائعة في كلمات المرور.<br>
        </div>
    """
    attacks_info_output.value = attacks_info

analyze_button.on_click(on_analyze_button_clicked)

# عرض عناصر واجهة المستخدم بتنسيق أبسط مع تخفيف المعايير
display(
    widgets.VBox([
        password_input,
        analyze_button,
        strong_password_message,
        results_output,
        strength_feedback_output,
        suggestions_output,
        attacks_info_output
    ])
)