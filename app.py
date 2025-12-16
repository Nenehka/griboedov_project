from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import tempfile
from werkzeug.utils import secure_filename
from utils import predict_mushroom, load_model_and_indices

# Инициализация Flask
app = Flask(__name__)

# Конфигурация
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Максимальный размер файла 16MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}


def allowed_file(filename):
    """Проверяет, что файл имеет разрешенное расширение"""
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Главная страница с формой загрузки"""
    return render_template('index.html')


@app.route('/api/predict', methods=['POST'])
def api_predict():
    """API endpoint для предсказания вида гриба"""

    # Проверяем, есть ли файл в запросе
    if 'file' not in request.files:
        return jsonify({
            'success': False,
            'error': 'Файл не найден в запросе'
        }), 400

    file = request.files['file']

    # Проверяем, что файл выбран
    if file.filename == '':
        return jsonify({
            'success': False,
            'error': 'Файл не выбран'
        }), 400

    # Проверяем расширение файла
    if not allowed_file(file.filename):
        return jsonify({
            'success': False,
            'error': 'Неподдерживаемый формат файла. Разрешены: png, jpg, jpeg, gif, bmp'
        }), 400

    # Сохраняем файл во временную директорию
    try:
        # Создаем временный файл
        temp_fd, temp_path = tempfile.mkstemp(suffix='.jpg')
        os.close(temp_fd)

        # Сохраняем загруженный файл
        file.save(temp_path)

        # Делаем предсказание
        result = predict_mushroom(temp_path)

        # Удаляем временный файл
        os.unlink(temp_path)

        # Добавляем статус успеха
        result['success'] = True

        return jsonify(result)

    except Exception as e:
        # Удаляем временный файл, если он существует
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.unlink(temp_path)

        return jsonify({
            'success': False,
            'error': f'Ошибка при обработке изображения: {str(e)}'
        }), 500


@app.route('/static/<path:path>')
def send_static(path):
    """Отдает статические файлы"""
    return send_from_directory('static', path)


if __name__ == '__main__':
    # Запускаем приложение
    app.run(debug=True, host='0.0.0.0', port=5000)