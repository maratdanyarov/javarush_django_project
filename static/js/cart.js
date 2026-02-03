// Функция для получения CSRF-токена
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.addEventListener('DOMContentLoaded', function () {
    console.log("Cart JS Loaded"); // Проверка в консоли (F12)

    const csrftoken = getCookie('csrftoken');

    // 1. Кнопка "Добавить в корзину" (Страница товара)
    const addBtn = document.querySelector('.btn-add-to-cart');
    if (addBtn) {
        addBtn.addEventListener('click', function () {
            const productId = this.dataset.productId;
            const quantity = document.getElementById('product-quantity').value;

            fetch(`/cart/add/${productId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: new URLSearchParams({'quantity': quantity})
            })
                .then(res => res.json())
                .then(data => {
                    alert(data.message);
                    location.reload(); // Обновляем, чтобы увидеть счетчик в хедере
                });
        });
    }

    // 2. Управление в самой корзине (страница /cart/)
    const cartList = document.getElementById('cart-items-list');
    if (cartList) {
        cartList.addEventListener('click', function (e) {
            const btn = e.target.closest('button');
            if (!btn) return;

            const productId = btn.dataset.productId;
            const action = btn.dataset.action;
            const itemRow = btn.closest('.cart-item');

            // Удаление
            if (action === 'remove') {
                fetch(`/cart/remove/${productId}/`, {
                    method: 'POST',
                    headers: {'X-CSRFToken': csrftoken, 'X-Requested-With': 'XMLHttpRequest'}
                }).then(() => location.reload());
            }

            // Изменение количества (+ / -)
            if (action === 'increase' || action === 'decrease') {
                const qtySpan = itemRow.querySelector('.quantity-value-cart');
                let currentQty = parseInt(qtySpan.textContent);
                let newQty = (action === 'increase') ? currentQty + 1 : currentQty - 1;

                if (newQty > 0) {
                    fetch(`/cart/update/${productId}/`, {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': csrftoken,
                            'X-Requested-With': 'XMLHttpRequest'
                        },
                        body: new URLSearchParams({'quantity': newQty})
                    })
                        .then(res => res.json())
                        .then(data => {
                            if (data.status === 'success') {
                                // 1. Показываем уведомление
                                alert(data.message);

                                // 2. Находим счетчик в шапке
                                let badge = document.getElementById('cart-badge');

                                if (badge) {
                                    // Если счетчик уже есть, просто меняем цифру
                                    badge.textContent = data.cart_items_count;
                                } else {
                                    // Если товара не было и счетчика нет — просто обновим страницу один раз
                                    location.reload();
                                }
                            }
                        });

                } else {
                    alert('Количество не может быть меньше 1!');
                }
            }
        });
    }
});