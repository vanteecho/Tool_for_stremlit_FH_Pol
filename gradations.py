# gradations.py

# Універсальна шкала для відсоткових показників (BS, Satur_...)
PERCENT_SCALE = [
    {"max": 20, "label": "Дуже низько (0-20%)", "color": "#d73027"}, # Червоний
    {"max": 40, "label": "Низько (20-40%)", "color": "#f46d43"},     # Помаранчевий
    {"max": 60, "label": "Середньо (40-60%)", "color": "#fdae61"},  # Жовто-помаранчевий
    {"max": 80, "label": "Високо (60-80%)", "color": "#a6d96a"},    # Салатовий
    {"max": 1000, "label": "Дуже високо (>80%)", "color": "#1a9850"} # Зелений
]

GRADATIONS = {
    # --- ОНОВЛЕНІ pH ТА КИСЛОТНІСТЬ ---
    "pH Water": {
        "default": [
            {"max": 4.49, "label": "Дуже кисла", "color": "#a50026"},      # Глибокий червоний
            {"max": 5.09, "label": "Кисла", "color": "#d73027"},           # Червоний
            {"max": 5.69, "label": "Середньо кисла", "color": "#f46d43"},  # Червоно-помаранчевий
            {"max": 6.29, "label": "Слабо кисла", "color": "#fdae61"},     # Помаранчевий
            {"max": 7.29, "label": "Нейтральна", "color": "#1a9850"},      # Зелений
            {"max": 50.0, "label": "Лужна", "color": "#762a83"}            # ФІОЛЕТОВИЙ
        ]
    },
    "pH Salt (KCl)": {
        "default": [
            {"max": 4.1, "label": "Дуже сильнокислі", "color": "#a50026"}, # Глибокий червоний
            {"max": 4.5, "label": "Сильнокислі", "color": "#d73027"},      # Червоний
            {"max": 5.0, "label": "Середньокислі", "color": "#f46d43"},    # Червоно-помаранчевий
            {"max": 5.5, "label": "Слабокислі", "color": "#fdae61"},       # Помаранчевий
            {"max": 6.0, "label": "Близькі до нейтральних", "color": "#a6d96a"}, # Жовто-зелений
            {"max": 7.0, "label": "Нейтральні", "color": "#1a9850"},       # Зелений
            {"max": 14.0, "label": "Лужні", "color": "#762a83"}            # ФІОЛЕТОВИЙ
        ]
    },
    "Hydrolytic Acidity": {
        # Тут шкала зворотна: менше значення = краще (зеленіше)
        "mg_eq_100g": [
            {"max": 2.0, "label": "Нейтральні", "color": "#006837"},       # Темно-зелений (найкраще)
            {"max": 3.0, "label": "Близькі до нейтрал", "color": "#1a9850"}, # Зелений
            {"max": 4.0, "label": "Слабокислі", "color": "#a6d96a"},       # Салатовий
            {"max": 5.0, "label": "Середньокислі", "color": "#fdae61"},    # Помаранчевий
            {"max": 6.01, "label": "Сильнокислі", "color": "#d73027"},     # Червоний
            {"max": 100.0, "label": "Дуже сильнокислі", "color": "#a50026"} # Глибокий червоний (найгірше)
        ],
        "default": [
            {"max": 2.0, "label": "Нейтральні", "color": "#006837"},
            {"max": 3.0, "label": "Близькі до нейтрал", "color": "#1a9850"},
            {"max": 4.0, "label": "Слабокислі", "color": "#a6d96a"},
            {"max": 5.0, "label": "Середньокислі", "color": "#fdae61"},
            {"max": 6.01, "label": "Сильнокислі", "color": "#d73027"},
            {"max": 100.0, "label": "Дуже сильнокислі", "color": "#a50026"}
        ]
    },

    # --- ІНШІ ПОКАЗНИКИ (Без змін) ---
    "Potassium (K2O)": { 
        "kirsanov": [{"max": 40, "label": "Дуже низький", "color": "#d7191c"}, {"max": 80, "label": "Низький", "color": "#fdae61"}, {"max": 120, "label": "Середнє", "color": "#ffffbf"}, {"max": 170, "label": "Підвищений", "color": "#a6d96a"}, {"max": 250, "label": "Високий", "color": "#1a9641"}, {"max": 10000, "label": "Дуже високий", "color": "#006837"}],
        "chirikov": [{"max": 20, "label": "Дуже низький", "color": "#d7191c"}, {"max": 40, "label": "Низький", "color": "#fdae61"}, {"max": 80, "label": "Середнє", "color": "#ffffbf"}, {"max": 120, "label": "Підвищений", "color": "#a6d96a"}, {"max": 180, "label": "Високий", "color": "#1a9641"}, {"max": 10000, "label": "Дуже високий", "color": "#006837"}],
        "machigin": [{"max": 100, "label": "Дуже низький", "color": "#d7191c"}, {"max": 200, "label": "Низький", "color": "#fdae61"}, {"max": 300, "label": "Середнє", "color": "#ffffbf"}, {"max": 400, "label": "Підвищений", "color": "#a6d96a"}, {"max": 600, "label": "Високий", "color": "#1a9641"}, {"max": 10000, "label": "Дуже високий", "color": "#006837"}],
        "ac_method": [{"max": 40.0, "label": "Дуже низький", "color": "#d7191c"}, {"max": 80.0, "label": "Низький", "color": "#fdae61"}, {"max": 120.0, "label": "Середній", "color": "#ffffbf"}, {"max": 200.0, "label": "Високий", "color": "#a6d96a"}, {"max": 10000.0, "label": "Дуже високий", "color": "#1a9641"}],
        "default": [{"max": 100, "label": "Дуже низький", "color": "#d7191c"}, {"max": 200, "label": "Низький", "color": "#fdae61"}, {"max": 300, "label": "Середнє", "color": "#ffffbf"}, {"max": 400, "label": "Підвищений", "color": "#a6d96a"}, {"max": 600, "label": "Високий", "color": "#1a9641"}, {"max": 10000, "label": "Дуже високий", "color": "#006837"}]
    },
    "Phosphate (P2O5)": { 
        "kirsanov": [{"max": 25, "label": "Дуже низький", "color": "#d7191c"}, {"max": 50, "label": "Низький", "color": "#fdae61"}, {"max": 100, "label": "Середнє", "color": "#ffffbf"}, {"max": 150, "label": "Підвищений", "color": "#a6d96a"}, {"max": 250, "label": "Високий", "color": "#1a9641"}, {"max": 10000, "label": "Дуже високий", "color": "#006837"}],
        "chirikov": [{"max": 20, "label": "Дуже низький", "color": "#d7191c"}, {"max": 50, "label": "Низький", "color": "#fdae61"}, {"max": 100, "label": "Середнє", "color": "#ffffbf"}, {"max": 150, "label": "Підвищений", "color": "#a6d96a"}, {"max": 200, "label": "Високий", "color": "#1a9641"}, {"max": 10000, "label": "Дуже високий", "color": "#006837"}],
        "machigin": [{"max": 10, "label": "Дуже низький", "color": "#d7191c"}, {"max": 15, "label": "Низький", "color": "#fdae61"}, {"max": 30, "label": "Середнє", "color": "#ffffbf"}, {"max": 45, "label": "Підвищений", "color": "#a6d96a"}, {"max": 60, "label": "Високий", "color": "#1a9641"}, {"max": 10000, "label": "Дуже високий", "color": "#006837"}],
        "olsen": [{"max": 3, "label": "Дуже низький", "color": "#d7191c"}, {"max": 9, "label": "Низький", "color": "#fdae61"}, {"max": 16, "label": "Середнє", "color": "#ffffbf"}, {"max": 21, "label": "Підвищений", "color": "#a6d96a"}, {"max": 30, "label": "Високий", "color": "#1a9641"}, {"max": 10000, "label": "Дуже високий", "color": "#006837"}],
        "default": [{"max": 10, "label": "Дуже низький", "color": "#d7191c"}, {"max": 15, "label": "Низький", "color": "#fdae61"}, {"max": 30, "label": "Середнє", "color": "#ffffbf"}, {"max": 45, "label": "Підвищений", "color": "#a6d96a"}, {"max": 60, "label": "Високий", "color": "#1a9641"}, {"max": 10000, "label": "Дуже високий", "color": "#006837"}]
    },
    "Electrical Conductivity (EC)": {
        "ms_cm": [
            {"max": 1.6, "label": "Вплив відсутній", "color": "#1a9641"},
            {"max": 3.0, "label": "Зниження врожайності (чутливі)", "color": "#a6d96a"},
            {"max": 5.6, "label": "Зниження врожаю (значне)", "color": "#fdae61"},
            {"max": 100.0, "label": "Різке зниження врожайності", "color": "#d7191c"}
        ],
        "default": [
            {"max": 1.6, "label": "Вплив відсутній", "color": "#1a9641"},
            {"max": 3.0, "label": "Зниження врожайності (чутливі)", "color": "#a6d96a"},
            {"max": 5.6, "label": "Зниження врожаю (значне)", "color": "#fdae61"},
            {"max": 100.0, "label": "Різке зниження врожайності", "color": "#d7191c"}
        ]
    },
    "Nitrogen (N)": {
        "mg_kg": [{"max": 10.0, "label": "Дуже низький", "color": "#d7191c"}, {"max": 16.0, "label": "Низький", "color": "#fdae61"}, {"max": 25.0, "label": "Середній", "color": "#ffffbf"}, {"max": 30.0, "label": "Підвищений", "color": "#a6d96a"}, {"max": 35.0, "label": "Високий", "color": "#1a9641"}, {"max": 10000.0, "label": "Дуже високий", "color": "#006837"}],
        "default": [{"max": 10.0, "label": "Дуже низький", "color": "#d7191c"}, {"max": 16.0, "label": "Низький", "color": "#fdae61"}, {"max": 25.0, "label": "Середній", "color": "#ffffbf"}, {"max": 30.0, "label": "Підвищений", "color": "#a6d96a"}, {"max": 35.0, "label": "Високий", "color": "#1a9641"}, {"max": 10000.0, "label": "Дуже високий", "color": "#006837"}]
    },
    "Boron (B)": {
        "mg_kg": [{"max": 0.3, "label": "Дуже низький", "color": "#d7191c"}, {"max": 0.8, "label": "Низький", "color": "#fdae61"}, {"max": 1.5, "label": "Середній", "color": "#ffffbf"}, {"max": 3.0, "label": "Високий", "color": "#a6d96a"}, {"max": 150.0, "label": "Дуже високий", "color": "#1a9641"}],
        "default": [{"max": 0.3, "label": "Дуже низький", "color": "#d7191c"}, {"max": 0.8, "label": "Низький", "color": "#fdae61"}, {"max": 1.5, "label": "Середній", "color": "#ffffbf"}, {"max": 3.0, "label": "Високий", "color": "#a6d96a"}, {"max": 150.0, "label": "Дуже високий", "color": "#1a9641"}]
    },
    "Salinity (Засоленість)": {
        "default": [{"max": 3.0, "label": "Сильносолонцюваті", "color": "#d7191c"}, {"max": 6.0, "label": "Середньосолонцюваті", "color": "#fdae61"}, {"max": 10.0, "label": "Слабосолонцюваті", "color": "#a6d96a"}, {"max": 100.0, "label": "Несолонцюваті", "color": "#1a9641"}]
    },
    "Sum of Absorbed Bases (SVO)": {
        "mg_eq_100g": [{"max": 5.0, "label": "Дуже низький", "color": "#d7191c"}, {"max": 10.0, "label": "Низький", "color": "#fdae61"}, {"max": 15.0, "label": "Середній", "color": "#ffffbf"}, {"max": 20.0, "label": "Підвищений", "color": "#a6d96a"}, {"max": 30.0, "label": "Високий", "color": "#1a9641"}, {"max": 1000.0, "label": "Дуже високий", "color": "#006837"}],
        "default": [{"max": 5.0, "label": "Дуже низький", "color": "#d7191c"}, {"max": 10.0, "label": "Низький", "color": "#fdae61"}, {"max": 15.0, "label": "Середній", "color": "#ffffbf"}, {"max": 20.0, "label": "Підвищений", "color": "#a6d96a"}, {"max": 30.0, "label": "Високий", "color": "#1a9641"}, {"max": 1000.0, "label": "Дуже високий", "color": "#006837"}]
    },
    "Calcium (Ca)": {
        "mg_eq_100g": [{"max": 2.5, "label": "Дуже низька", "color": "#d7191c"}, {"max": 5.0, "label": "Низька", "color": "#fdae61"}, {"max": 10.0, "label": "Середня", "color": "#ffffbf"}, {"max": 15.0, "label": "Підвищена", "color": "#a6d96a"}, {"max": 20.0, "label": "Висока", "color": "#1a9641"}, {"max": 1000.0, "label": "Дуже висока", "color": "#006837"}],
        "mg_kg": [{"max": 500, "label": "Дуже низька", "color": "#d7191c"}, {"max": 1000, "label": "Низька", "color": "#fdae61"}, {"max": 2000, "label": "Середня", "color": "#ffffbf"}, {"max": 3000, "label": "Підвищена", "color": "#a6d96a"}, {"max": 4000, "label": "Висока", "color": "#1a9641"}, {"max": 100000, "label": "Дуже висока", "color": "#006837"}],
        "default": [{"max": 500, "label": "Дуже низька", "color": "#d7191c"}, {"max": 1000, "label": "Низька", "color": "#fdae61"}, {"max": 2000, "label": "Середня", "color": "#ffffbf"}, {"max": 3000, "label": "Підвищена", "color": "#a6d96a"}, {"max": 4000, "label": "Висока", "color": "#1a9641"}, {"max": 100000, "label": "Дуже висока", "color": "#006837"}]
    },
    "Magnesium (Mg)": {
        "mg_eq_100g": [{"max": 0.5, "label": "Дуже низька", "color": "#d7191c"}, {"max": 1.0, "label": "Низька", "color": "#fdae61"}, {"max": 2.0, "label": "Середня", "color": "#ffffbf"}, {"max": 3.0, "label": "Підвищена", "color": "#a6d96a"}, {"max": 4.0, "label": "Висока", "color": "#1a9641"}, {"max": 100.0, "label": "Дуже висока", "color": "#006837"}],
        "mg_kg": [{"max": 60, "label": "Дуже низька", "color": "#d7191c"}, {"max": 120, "label": "Низька", "color": "#fdae61"}, {"max": 240, "label": "Середня", "color": "#ffffbf"}, {"max": 360, "label": "Підвищена", "color": "#a6d96a"}, {"max": 480, "label": "Висока", "color": "#1a9641"}, {"max": 10000, "label": "Дуже висока", "color": "#006837"}],
        "default": [{"max": 60, "label": "Дуже низька", "color": "#d7191c"}, {"max": 120, "label": "Низька", "color": "#fdae61"}, {"max": 240, "label": "Середня", "color": "#ffffbf"}, {"max": 360, "label": "Підвищена", "color": "#a6d96a"}, {"max": 480, "label": "Висока", "color": "#1a9641"}, {"max": 10000, "label": "Дуже висока", "color": "#006837"}]
    },
    "Organic Matter": {
        "default": [{"max": 1.0, "label": "Дуже низький", "color": "#d7191c"}, {"max": 2.0, "label": "Низький", "color": "#fdae61"}, {"max": 4.0, "label": "Середній", "color": "#ffffbf"}, {"max": 6.0, "label": "Високий", "color": "#1a9641"}, {"max": 100.0, "label": "Дуже високий", "color": "#006837"}]
    },
    "Manganese (Mn)": { "default": [{"max": 3.0, "label": "дуже низький", "color": "#d7191c"}, {"max": 8.0, "label": "низький", "color": "#fdae61"}, {"max": 12.0, "label": "середній", "color": "#ffffbf"}, {"max": 30.0, "label": "високий", "color": "#1a9641"}, {"max": 500.0, "label": "дуже високий", "color": "#006837"}] },
    "Zinc (Zn)": { "default": [{"max": 0.25, "label": "дуже низький", "color": "#d7191c"}, {"max": 0.50, "label": "низький", "color": "#fdae61"}, {"max": 1.00, "label": "середній", "color": "#ffffbf"}, {"max": 10.00, "label": "високий", "color": "#1a9641"}, {"max": 100.00, "label": "дуже високий", "color": "#006837"}] },
    "Copper (Cu)": { "default": [{"max": 0.20, "label": "дуже низький", "color": "#d7191c"}, {"max": 0.80, "label": "низький", "color": "#fdae61"}, {"max": 1.20, "label": "середній", "color": "#ffffbf"}, {"max": 2.50, "label": "високий", "color": "#1a9641"}, {"max": 100.00, "label": "дуже високий", "color": "#006837"}] },
    "Iron (Fe)": { "default": [{"max": 4.0, "label": "дуже низький", "color": "#d7191c"}, {"max": 10.0, "label": "низький", "color": "#fdae61"}, {"max": 16.0, "label": "середній", "color": "#ffffbf"}, {"max": 25.0, "label": "високий", "color": "#1a9641"}, {"max": 500.0, "label": "дуже високий", "color": "#006837"}] },
    "Sodium (Na)": { "default": [{"max": 10, "label": "Низький", "color": "#d7191c"}, {"max": 30, "label": "Середній", "color": "#ffffbf"}, {"max": 1000, "label": "Високий", "color": "#1a9641"}] },
    "Percentage Scale": { "default": PERCENT_SCALE }
}