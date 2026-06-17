from flask import Flask, jsonify, request

app = Flask(__name__)

patients = [
    {
        "patient_id": "P001",
        "personal_info": {
            "first_name": "Елена",
            "last_name": "Смирнова",
            "middle_name": "Андреевна",
            "birth_date": "1985-06-12",
            "gender": "female",
            "blood_type": "A+"
        },
        "contact": {
            "phone": "+7 (999) 111-22-33",
            "email": "e.smirnova@email.com",
            "address": "ул. Ленина, д. 10, кв. 45"
        },
        "medical": {
            "diagnosis": "Бронхиальная астма",
            "allergies": ["пыльца", "кошачья шерсть"],
            "chronic_diseases": ["аллергия"],
            "current_medications": ["Сальбутамол", "Пульмикорт"]
        },
        "admission": {
            "date": "2024-03-01",
            "department": "Пульмонология",
            "doctor": "др. Волков",
            "emergency_contact": "+7 (999) 777-88-99"
        },
        "errors": {
            "error": " ",
            "error_code": " "
        }
    },
    {
        "patient_id": "P002",
        "personal_info": {
            "first_name": "Дмитрий",
            "last_name": "Козлов",
            "middle_name": "Сергеевич",
            "birth_date": "1972-11-23",
            "gender": "male",
            "blood_type": "O-"
        },
        "contact": {
            "phone": "+7 (999) 222-33-44",
            "email": "d.kozlov@email.com",
            "address": "пр. Мира, д. 5, кв. 123"
        },
        "medical": {
            "diagnosis": "Ишемическая болезнь сердца",
            "allergies": ["пенициллин"],
            "chronic_diseases": ["гипертония", "атеросклероз"],
            "current_medications": ["Аспирин", "Эналаприл"]
        },
        "admission": {
            "date": "2024-02-15",
            "department": "Кардиология",
            "doctor": "др. Соколова",
            "emergency_contact": "+7 (999) 888-99-00"
        },
        "errors": {
            "error": "",
            "error_code": ""
        }
    },
    {
        "patient_id": "P003",
        "personal_info": {
            "first_name": "Елена",
            "last_name": "Смирнова",
            "middle_name": "Андреевна",
            "birth_date": "1985-06-12",
            "gender": "female",
            "blood_type": "A+"
        },
        "contact": {
            "phone": "+7 (999) 111-22-33",
            "email": "e.smirnova@email.com",
            "address": "ул. Ленина, д. 10, кв. 45"
        },
        "medical": {
            "diagnosis": "Бронхиальная астма",
            "allergies": ["пыльца", "кошачья шерсть"],
            "chronic_diseases": ["аллергия"],
            "current_medications": ["Сальбутамол", "Пульмикорт"]
        },
        "admission": {
            "date": "2024-03-01",
            "department": "Пульмонология",
            "doctor": "др. Волков",
            "emergency_contact": "+7 (999) 777-88-99"
        },
        "errors": {
            "error": "",
            "error_code": ""
        }
    },
    {
        "patient_id": "P004",
        "personal_info": {
            "first_name": "Дмитрий",
            "last_name": "Козлов",
            "middle_name": "Сергеевич",
            "birth_date": "1972-11-23",
            "gender": "male",
            "blood_type": "O-"
        },
        "contact": {
            "phone": "+7 (999) 222-33-44",
            "email": "d.kozlov@email.com",
            "address": "пр. Мира, д. 5, кв. 123"
        },
        "medical": {
            "diagnosis": "Ишемическая болезнь сердца",
            "allergies": ["пенициллин"],
            "chronic_diseases": ["гипертония", "атеросклероз"],
            "current_medications": ["Аспирин", "Эналаприл"]
        },
        "admission": {
            "date": "2024-02-15",
            "department": "Кардиология",
            "doctor": "др. Соколова",
            "emergency_contact": "+7 (999) 888-99-00"
        },
        "errors": {
            "error": "ИУМК",
            "error_code": "1"
        }
    },
    {
        "patient_id": "P005",
        "personal_info": {
            "first_name": "Елена",
            "last_name": "Смирнова",
            "middle_name": "Андреевна",
            "birth_date": "1985-06-12",
            "gender": "female",
            "blood_type": "A+"
        },
        "contact": {
            "phone": "+7 (999) 111-22-33",
            "email": "e.smirnova@email.com",
            "address": "ул. Ленина, д. 10, кв. 45"
        },
        "medical": {
            "diagnosis": "Бронхиальная астма",
            "allergies": ["пыльца", "кошачья шерсть"],
            "chronic_diseases": ["аллергия"],
            "current_medications": ["Сальбутамол", "Пульмикорт"]
        },
        "admission": {
            "date": "2024-03-01",
            "department": "Пульмонология",
            "doctor": "др. Волков",
            "emergency_contact": "+7 (999) 777-88-99"
        },
        "errors": {
            "error": "",
            "error_code": "132"
        }
    },
    {
        "patient_id": "P006",
        "personal_info": {
            "first_name": "Дмитрий",
            "last_name": "Козлов",
            "middle_name": "Сергеевич",
            "birth_date": "1972-11-23",
            "gender": "male",
            "blood_type": "O-"
        },
        "contact": {
            "phone": "+7 (999) 222-33-44",
            "email": "d.kozlov@email.com",
            "address": "пр. Мира, д. 5, кв. 123"
        },
        "medical": {
            "diagnosis": "Ишемическая болезнь сердца",
            "allergies": ["пенициллин"],
            "chronic_diseases": ["гипертония", "атеросклероз"],
            "current_medications": ["Аспирин", "Эналаприл"]
        },
        "admission": {
            "date": "2024-02-15",
            "department": "Кардиология",
            "doctor": "др. Соколова",
            "emergency_contact": "+7 (999) 888-99-00"
        },
        "errors": {
            "error": "ИУМК",
            "error_code": "12"
        }
    }
]

@app.route('/patients', methods=['GET'])
def get_patients():
    return jsonify(patients)

@app.route('/patients', methods=['POST'])
def add_patient():
    """Добавляет нового пациента в список."""
    new_patient = request.get_json()
    if not new_patient:
        return jsonify({"error": "No input data provided"}), 400
    if not isinstance(new_patient, dict):
        return jsonify({"error": "Invalid data format, expected a JSON object"}), 400
    patients.append(new_patient)
    return jsonify(new_patient), 201

@app.route('/patients/<string:patient_id>', methods=['PUT'])
def update_patient(patient_id):
    """Обновляет существующего пациента по patient_id."""
    updated_data = request.get_json()
    if not updated_data:
        return jsonify({"error": "No input data provided"}), 400
    if not isinstance(updated_data, dict):
        return jsonify({"error": "Invalid data format, expected a JSON object"}), 400

    # Ищем пациента по ID
    for index, patient in enumerate(patients):
        if patient.get('patient_id') == patient_id:
            # Заменяем запись целиком (можно также частично обновить, но здесь полная замена)
            # Убедимся, что ID не меняется (если в теле передан другой ID, используем URL)
            updated_data['patient_id'] = patient_id
            patients[index] = updated_data
            return jsonify(updated_data), 200

    return jsonify({"error": f"Patient with id {patient_id} not found"}), 404

@app.route('/patients/<string:patient_id>', methods=['DELETE'])
def delete_patient(patient_id):
    """Удаляет пациента по patient_id."""
    for index, patient in enumerate(patients):
        if patient.get('patient_id') == patient_id:
            deleted = patients.pop(index)
            return jsonify({"message": f"Patient {patient_id} deleted successfully", "deleted": deleted}), 200

    return jsonify({"error": f"Patient with id {patient_id} not found"}), 404

if __name__ == '__main__':
    app.run(debug=True, host='83.217.28.113', port=5000)
