import streamlit as st
import string
import random
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Dropout

# بيانات التدريب
common_passwords = ["123456", "password", "qwerty", "admin", "user"]
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

def analyze_password_strength(password):
    features = np.zeros((1, len(password), n_chars))
    for i, char in enumerate(password):
        if char in char_to_int:
            features[0, i, char_to_int[char]] = 1
    strength_model = model.predict(features, verbose=0)[0][0]

    score = 0
    if len(password) >= 8:
        score += 1
    if any(c.islower() for c in password):
        score += 1
    if any(c.isupper() for c in password):
        score += 1
    if any(c.isdigit() for c in password):
        score += 1
    if any(c in string.punctuation for c in password):
        score += 1

    manual_strength = score / 5
    final_score = (strength_model + manual_strength) / 2

    if final_score >= 0.8:
        return "جيدة ✅"
    elif final_score >= 0.5:
        return "مقبولة ⚠️"
    else:
        return "ضعيفة ❌"

# واجهة Streamlit
st.title("🔐 تحليل قوة كلمة المرور")
password = st.text_input("أدخل كلمة المرور هنا", type="password")

if password:
    strength = analyze_password_strength(password)
    st.markdown(f"### النتيجة: {strength}")
    if password in common_passwords:
        st.warning("⚠️ كلمة المرور هذه شائعة جدًا! اختر كلمة مرور فريدة.")
