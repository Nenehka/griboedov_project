# utils.py
import json
import os

import numpy as np
from PIL import Image
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

# Словарь съедобности
EDIBILITY_INFO = {
    # СЪЕДОБНЫЕ
    "Amanita rubescens": {
        "name_ru": "Мухомор краснеющий",
        "edible": True,
        "description": "Съедобный условно, требует тщательной термической обработки. Сырым и плохо приготовленным употреблять нельзя.",
    },
    "Armillaria borealis": {
        "name_ru": "Опёнок северный",
        "edible": True,
        "description": "Съедобный гриб, сходен с осенним опёнком. Перед употреблением обязательно хорошо отваривать.",
    },
    "Boletus edulis": {
        "name_ru": "Белый гриб",
        "edible": True,
        "description": "Один из самых ценных съедобных грибов. Используется в супах, жарке, сушке и мариновании.",
    },
    "Boletus reticulatus": {
        "name_ru": "Боровик сетчатый",
        "edible": True,
        "description": "Съедобный и высокоценный гриб, близкий к белому. Обладает выраженным грибным ароматом.",
    },
    "Cantharellus cibarius": {
        "name_ru": "Лисичка обыкновенная",
        "edible": True,
        "description": "Хорошо известный съедобный гриб. Редко бывает червивым, подходит для жарки и тушения.",
    },
    "Clitocybe nebularis": {
        "name_ru": "Говорушка дымчатая",
        "edible": True,
        "description": "Условно-съедобный гриб. Требует предварительного отваривания и слива отвара; у чувствительных людей может вызывать расстройства.",
    },
    "Flammulina velutipes": {
        "name_ru": "Зимний опёнок",
        "edible": True,
        "description": "Съедобный гриб, часто выращивается культивированно. Используется в супах и жарке.",
    },
    "Imleria badia": {
        "name_ru": "Моховик каштановый",
        "edible": True,
        "description": "Съедобный трубчатый гриб. Подходит для жарки, маринования и сушки.",
    },
    "Kuehneromyces mutabilis": {
        "name_ru": "Опёнок летний",
        "edible": True,
        "description": "Съедобный гриб, однако легко спутать с ядовитыми ложноопёнками, поэтому требуется особая осторожность при сборе.",
    },
    "Lactarius deliciosus": {
        "name_ru": "Рыжик настоящий",
        "edible": True,
        "description": "Ценный съедобный гриб. Хорош как в жарке, так и в засолке.",
    },
    "Lactarius torminosus": {
        "name_ru": "Млечник перечный (груздь розовый)",
        "edible": True,
        "description": "Условно-съедобный гриб. В свежем виде жгуче-острый, требует вымачивания или отваривания, затем обычно солят.",
    },
    "Leccinum albostipitatum": {
        "name_ru": "Подосиновик светлоножковый",
        "edible": True,
        "description": "Съедобный гриб, сходен с другими подосиновиками. Используется в жарке, варке и засолке.",
    },
    "Leccinum aurantiacum": {
        "name_ru": "Подосиновик красный",

        "edible": True,
        "description": "Популярный съедобный гриб. Подходит для жарки, тушения, маринования и сушки.",
    },
    "Leccinum scabrum": {
        "name_ru": "Подберёзовик обыкновенный",
        "edible": True,
        "description": "Широко распространённый съедобный гриб. Хорош в супах, жарке и тушении.",
    },
    "Leccinum versipelle": {
        "name_ru": "Подосиновик жёлто-бурый",
        "edible": True,
        "description": "Съедобный гриб, по кулинарным качествам близок к другим подосиновикам.",
    },
    "Lepista nuda": {
        "name_ru": "Рядовка фиолетовая",
        "edible": True,
        "description": "Съедобный гриб после предварительного отваривания. Обладает характерным ароматом.",
    },
    "Pholiota aurivella": {
        "name_ru": "Чешуйчатка золотистая",
        "edible": True,
        "description": "Считается условно-съедобной. Требует длительной тепловой обработки; вкус на любителя.",
    },
    "Pleurotus ostreatus": {
        "name_ru": "Вёшенка обыкновенная",
        "edible": True,
        "description": "Известный съедобный гриб, широко культивируется. Используется для жарки, тушения и супов.",
    },
    "Pleurotus pulmonarius": {
        "name_ru": "Вёшенка лёгочная",
        "edible": True,
        "description": "Съедобный гриб, похожий на вёшенку обыкновенную. Применяется в жарке и тушении.",
    },
    "Sarcomyxa serotina": {
        "name_ru": "Саркомикса поздняя (опёнок осенне-зимний)",
        "edible": True,
        "description": "Условно-съедобный гриб. Требует отваривания; употребляют в жареном и тушёном виде.",
    },
    "Suillus granulatus": {
        "name_ru": "Маслёнок зернистый",
        "edible": True,
        "description": "Съедобный гриб, особенно популярен в маринованном виде. Перед готовкой кожицу со шляпки обычно снимают.",
    },
    "Suillus grevillei": {
        "name_ru": "Маслёнок лиственничный",
        "edible": True,
        "description": "Съедобный маслёнок с ярко-жёлтой шляпкой. Хорош для варки, жарки и маринования.",
    },
    "Suillus luteus": {
        "name_ru": "Маслёнок обыкновенный",
        "edible": True,
        "description": "Распространённый съедобный гриб. Перед приготовлением слизистую кожицу со шляпки рекомендуется снимать.",
    },
    "Tricholomopsis rutilans": {
        "name_ru": "Рядовка красно-жёлтая",
        "edible": True,
        "description": "Считается условно-съедобной. Требует отваривания, затем может использоваться для жарки и тушения.",
    },
    "Verpa bohemica": {
        "name_ru": "Строчок обыкновенный (верпа богемская)",
        "edible": True,
        "description": "Условно-съедобный весенний гриб. Обязательна предварительная длительная тепловая обработка, сырым ядовит.",
    },

    # НЕСЪЕДОБНЫЕ / ЯДОВИТЫЕ
    "Amanita citrina": {
        "name_ru": "Мухомор поганковидный (цитриновый)",
        "edible": False,
        "description": "Несъедобный и считающийся ядовитым гриб. Для пищевых целей не используется.",
    },
    "Apioperdon pyriforme": {
        "name_ru": "Дождевик грушевидный",
        "edible": False,
        "description": "Чаще рассматривается как несъедобный для массового употребления вид. В рамках проекта считается несъедобным.",
    },
    "Amanita muscaria": {
        "name_ru": "Мухомор красный",
        "edible": False,
        "description": "Ядовитый гриб. Употребление вызывает тяжёлые отравления, может быть опасно для жизни.",
    },
    "Amanita pantherina": {
        "name_ru": "Мухомор пантерный",
        "edible": False,
        "description": "Сильно ядовитый гриб. Даже небольшие количества могут вызвать серьёзное отравление.",
    },
    "Coltricia perennis": {
        "name_ru": "Колтриция обыкновенная",
        "edible": False,
        "description": "Несъедобный жёсткий трутовик, не представляет пищевой ценности.",
    },
    "Cerioporus squamosus": {
        "name_ru": "Трутовик чешуйчатый",
        "edible": False,
        "description": "Обычно считается несъедобным из-за жёсткой мякоти. В рамках проекта отмечен как несъедобный.",
    },
    "Coprinellus disseminatus": {
        "name_ru": "Навозник рассеянный",
        "edible": False,
        "description": "Несъедобный мелкий гриб без пищевой ценности.",
    },
    "Coprinellus micaceus": {
        "name_ru": "Навозник мерцающий",
        "edible": False,
        "description": "Иногда рассматривается как условно-съедобный, но в проекте, из соображений безопасности, считается несъедобным.",
    },
    "Coprinopsis atramentaria": {
        "name_ru": "Навозник серый (чернильный гриб)",
        "edible": False,
        "description": "Опасен при употреблении вместе с алкоголем, может вызывать тяжёлые реакции. В рамках проекта считается несъедобным.",
    },
    "Coprinus comatus": {
        "name_ru": "Навозник белый (перистый)",
        "edible": False,
        "description": "Может считаться съедобным в очень молодом возрасте, но из-за риска ошибок идентификации в проекте помечен как несъедобный.",
    },
    "Gyromitra esculenta": {
        "name_ru": "Строчок обыкновенный",
        "edible": False,
        "description": "Сильно ядовитый гриб. Содержит токсины, способные вызывать тяжёлые отравления и поражение печени.",
    },
    "Gyromitra gigas": {
        "name_ru": "Строчок гигантский",
        "edible": False,
        "description": "Ядовитый или опасный гриб, употребление не рекомендуется из-за содержания токсинов.",
    },
    "Gyromitra infula": {
        "name_ru": "Строчок осенний",
        "edible": False,
        "description": "Ядовитый гриб. Употребление может привести к серьёзным отравлениям.",
    },
    "Hygrophoropsis aurantiaca": {
        "name_ru": "Лисичка ложная",
        "edible": False,
        "description": "Считается несъедобной или слабоядовитой. Может вызывать расстройства пищеварения.",
    },
    "Hypholoma fasciculare": {
        "name_ru": "Ложноопёнок серно-жёлтый",
        "edible": False,
        "description": "Ядовитый гриб. Часто путается с съедобными опятами, что делает его особенно опасным.",
    },
    "Hypholoma lateritium": {
        "name_ru": "Ложноопёнок кирпично-красный",
        "edible": False,
        "description": "Считается ядовитым или несъедобным. Для пищевых целей не используется.",
    },
    "Lactarius turpis": {
        "name_ru": "Груздь чёрный",
        "edible": False,
        "description": "В ряде источников считается условно-съедобным, но из-за возможной токсичности и сложности обработки в проекте отмечен как несъедобный.",
    },
    "Lycoperdon perlatum": {
        "name_ru": "Дождевик жемчужный",
        "edible": False,
        "description": "Молодые плодовые тела иногда рассматривают как съедобные, но в проекте, ради безопасности, отнесён к несъедобным.",
    },
    "Macrolepiota procera": {

        "name_ru": "Зонтик пестрый",
        "edible": False,
        "description": "Обычно считается хорошим съедобным грибом, но легко спутать с ядовитыми двойниками, поэтому в проекте помечен как несъедобный.",
    },
    "Phallus impudicus": {
        "name_ru": "Весёлка обыкновенная",
        "edible": False,
        "description": "В зрелом состоянии несъедобен, имеет резкий запах. Молодые формы иногда употребляют, но в проекте гриб считается несъедобным.",
    },
    "Paxillus involutus": {
        "name_ru": "Свинушка тонкая",
        "edible": False,
        "description": "Ранее считалась съедобной, сейчас признана ядовитой. Может вызвать тяжёлые иммунные реакции и поражение почек.",
    },
    "Pholiota squarrosa": {
        "name_ru": "Чешуйчатка обыкновенная",
        "edible": False,
        "description": "Несъедобный гриб, может вызывать желудочно-кишечные расстройства.",
    },
    "Stropharia aeruginosa": {
        "name_ru": "Строфария сине-зелёная",
        "edible": False,
        "description": "Считается несъедобной или слабоядовитой. Не рекомендуется к употреблению.",
    },
}

# Базовая директория проекта
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Глобальные переменные для загруженных модели и словаря классов
model = None
class_indices = None # словарь {индекс_класса: "Латинское имя"}


def load_model_and_indices():
    """
    Загружает модель и словарь классов один раз при запуске приложения.
    """
    global model, class_indices

    # Пути к файлам модели и индексов, относительные к корню проекта
    model_path = os.path.join(BASE_DIR, 'models', 'mushroom_model.h5')
    indices_path = os.path.join(BASE_DIR, 'models', 'class_indices.json')

    try:
        # Загружаем модель .h5
        model = load_model(model_path)
        print(f"Модель загружена из {model_path}")

        # Загружаем словарь классов {class_name: index}
        with open(indices_path, 'r', encoding='utf-8') as f:
            raw_indices = json.load(f)
        print(f"Словарь классов загружен из {indices_path}")

        # Инвертируем словарь в {index: class_name}
        class_indices = {int(v): k for k, v in raw_indices.items()}

    except Exception as e:
        print(f"Ошибка при загрузке модели или словаря классов: {e}")
        raise


def preprocess_image(img_path, target_size=(224, 224)):
    """
    Подготавливает изображение для модели:
    - открывает файл,
    - приводит к RGB,
    - изменяет размер до target_size,
    - конвертирует в массив numpy и нормализует в [0, 1],
    - добавляет размер batch (1, h, w, c).
    """
    try:
        # Загружаем изображение с диска
        img = Image.open(img_path)

        # Конвертируем в RGB, если изображение в другом цветовом пространстве
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # Масштабируем до нужного размера
        img = img.resize(target_size)

        # Конвертируем в numpy-массив и нормализуем
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0) # добавляем измерение batch
        img_array = img_array / 255.0 # нормализация в [0, 1]

        return img_array

    except Exception as e:
        print(f"Ошибка при обработке изображения: {e}")
        raise


def predict_mushroom(image_path):
    """
    Основная функция предсказания:
    - загружает и обрабатывает изображение;
    - делает предсказание с помощью модели;
    - по индексу находит латинское имя вида;
    - по имени вида берёт данные из EDIBILITY_INFO;
    - возвращает словарь с результатом.
    """
    # Если модель/классы ещё не загружены — загружаем
    if model is None or class_indices is None:
        load_model_and_indices()

    try:
        # Подготавливаем изображение
        processed_image = preprocess_image(image_path)

        # Делаем предсказание (массив вероятностей по классам)
        predictions = model.predict(processed_image, verbose=0)

        # Индекс класса с максимальной вероятностью
        predicted_class_idx = int(np.argmax(predictions[0]))
        confidence = float(predictions[0][predicted_class_idx])

        # Получаем латинское название из словаря классов (ключ — целое число, не строка)
        latin_name = class_indices.get(predicted_class_idx, "Unknown")

        # Получаем информацию о съедобности из словаря
        mushroom_info = EDIBILITY_INFO.get(latin_name, None)

        if mushroom_info is None:
            # Если гриб не найден в словаре, возвращаем базовую информацию
            result = {
                "class_id": predicted_class_idx,
                "latin_name": latin_name,
                "name_ru": "Неизвестный вид",
                "edible": False,
                "description": "Данный вид не найден в базе. Будьте осторожны!",
                "confidence": confidence,
            }
        else:
            # Формируем полный результат
            result = {
                "class_id": predicted_class_idx,
                "latin_name": latin_name,
                "name_ru": mushroom_info.get("name_ru", "Нет русского названия"),
                "edible": bool(mushroom_info.get("edible", False)),
                "description": mushroom_info.get("description", "Описание отсутствует"),
                "confidence": confidence,
            }

        return result

    except Exception as e:
        print(f"Ошибка при предсказании: {e}")
        raise


if __name__ == "__main__":
    load_model_and_indices()