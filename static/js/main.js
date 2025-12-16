document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('fileInput');
    const uploadBtn = document.getElementById('uploadBtn');
    const uploadBtnText = document.getElementById('uploadBtnText');

    const imagePreview = document.getElementById('imagePreview');
    const resultContainer = document.getElementById('resultContainer');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const predictionResult = document.getElementById('predictionResult');

    const memoBtn = document.getElementById('memoBtn');
    const memoOverlay = document.getElementById('memoOverlay');
    const memoClose = document.getElementById('memoClose');

    // Логика загрузки/предсказания

    // Открываем диалог выбора файла
    uploadBtn.addEventListener('click', () => {
        fileInput.click();
    });

    // Когда пользователь выбрал файл
    fileInput.addEventListener('change', () => {
        const file = fileInput.files[0];
        if (!file) return;

        // Предпросмотр
        const reader = new FileReader();
        reader.onload = (e) => {
            imagePreview.innerHTML = `<img src="${e.target.result}" alt="Фото гриба">`;
        };
        reader.readAsDataURL(file);

        // Отправляем файл на сервер
        sendRequest(file);
    });

    function sendRequest(file) {
        const formData = new FormData();
        formData.append('file', file);

        setLoading(true);

        fetch('/api/predict', {
            method: 'POST',
            body: formData
        })
            .then(async (response) => {
                let data;
                try {
                    data = await response.json();
                } catch (e) {
                    throw new Error('Сервер вернул некорректный ответ.');
                }

                if (!response.ok) {
                    const message = data && data.error ? data.error : 'Ошибка на сервере.';
                    throw new Error(message);
                }

                return data;
            })
            .then((data) => {
                if (!data.success) {
                    const msg = data.error || 'Не удалось получить предсказание.';
                    showError(msg);
                    return;
                }
                showResult(data);
            })
            .catch((error) => {
                showError(error.message || 'Произошла неизвестная ошибка.');
            })
            .finally(() => {
                setLoading(false);
            });
    }

    function setLoading(isLoading) {
        if (isLoading) {
            loadingSpinner.classList.remove('hidden');
            predictionResult.classList.add('hidden');
            resultContainer.classList.add('hidden');
            uploadBtn.disabled = true;
        } else {
            loadingSpinner.classList.add('hidden');
            uploadBtn.disabled = false;
        }
    }

    function showError(message) {
        predictionResult.classList.remove('hidden');
        resultContainer.classList.add('hidden');

        uploadBtnText.textContent = 'Загрузить фото';

        predictionResult.innerHTML = `
            <div class="result-error">
                <p class="result-title">Ошибка</p>
                <p class="result-description">
                    ${escapeHtml(message)}
                </p>
            </div>
        `;
    }

    function showResult(data) {
        const edible = !!data.edible;
        const nameRu = data.name_ru || 'Неизвестный вид';
        const description = data.description || 'Описание отсутствует.';
        const edibleText = edible ? 'Съедобный' : 'НЕ съедобный';
        const edibleClass = edible ? 'edible-text' : 'inedible-text';

        // Процент уверенности
        const confidence = (typeof data.confidence === 'number') ? data.confidence : 0;
        const confidencePercent = Math.round(confidence * 100);

        predictionResult.classList.remove('hidden');
        resultContainer.classList.add('hidden');

        uploadBtnText.textContent = 'Загрузить ещё';

        predictionResult.innerHTML = `
            <div>
                <p class="result-title">${escapeHtml(nameRu)}</p>
                <p class="result-edible ${edibleClass}">
                    ${escapeHtml(edibleText)}
                </p>
                <p class="result-description">
                    ${escapeHtml(description)}
                </p>
                <p class="confidence-text">
                    Уверенность модели:&nbsp;
                    <span>${confidencePercent}%</span>
                </p>
            </div>
        `;
    }

    function escapeHtml(text) {
        if (typeof text !== 'string') return text;
        return text
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    // Модалка Памятка

    memoBtn.addEventListener('click', () => {
        memoOverlay.classList.remove('hidden');
    });

    memoClose.addEventListener('click', () => {
        memoOverlay.classList.add('hidden');
    });

    // Клик по фону закрывает окно
    memoOverlay.addEventListener('click', (event) => {
        if (event.target === memoOverlay) {
            memoOverlay.classList.add('hidden');
        }
    });
});