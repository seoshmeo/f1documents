// Webhook Configuration
const WEBHOOK_CONFIG = {
    // Production webhook
    url: 'https://n8n.idontcareaboutname.ru/webhook/ae7e6e72-80f7-447b-b37a-cf9da952789f'

    // Test webhook - use while testing
    // url: 'https://n8n.idontcareaboutname.ru/webhook-test/ae7e6e72-80f7-447b-b37a-cf9da952789f'
};

// Notification System
function showNotification(type, title, message) {
    const notification = document.getElementById('notification');
    const titleEl = notification.querySelector('.notification__title');
    const messageEl = notification.querySelector('.notification__message');

    // Remove previous type classes
    notification.classList.remove('notification--success', 'notification--error');

    // Add new type class
    notification.classList.add(`notification--${type}`);

    // Set content
    titleEl.textContent = title;
    messageEl.textContent = message;

    // Show notification
    notification.classList.add('show');

    // Hide after 5 seconds
    setTimeout(() => {
        notification.classList.remove('show');
    }, 5000);
}

function showSuccess(title, message) {
    showNotification('success', title, message);
}

function showError(title, message) {
    showNotification('error', title, message);
}

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Scroll to calculator function
function scrollToCalculator() {
    const calculator = document.getElementById('calculator');
    if (calculator) {
        calculator.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

// Calculator functionality
function calculatePrice() {
    const area = parseFloat(document.getElementById('area').value);
    const typeSelect = document.getElementById('type');
    const type = parseFloat(typeSelect.value);
    const complexity = parseFloat(document.getElementById('complexity').value);
    const lighting = parseFloat(document.getElementById('lighting').value);
    const quantity = parseInt(document.getElementById('quantity').value) || 1;

    const displayType = document.getElementById('display-type');
    const displayTotal = document.getElementById('display-total');
    const resultDiv = document.getElementById('result');

    if (!area || area <= 0) {
        resultDiv.innerHTML = '<p style="color: #EF4444; font-weight: 600;">Пожалуйста, укажите площадь помещения</p>';
        return;
    }

    if (!type) {
        resultDiv.innerHTML = '<p style="color: #EF4444; font-weight: 600;">Пожалуйста, выберите тип потолка</p>';
        return;
    }

    // Calculate base price
    let basePrice = area * type;

    // Apply complexity multiplier
    if (complexity > 0) {
        basePrice = basePrice * (1 + complexity / 100);
    }

    // Add lighting cost
    let lightingCost = 0;
    if (lighting > 0) {
        if (lighting === 2500) {
            // LED lighting per meter
            lightingCost = lighting * Math.sqrt(area);
        } else {
            // Chandelier or spotlights
            lightingCost = lighting * quantity;
        }
    }

    const totalPrice = Math.round(basePrice + lightingCost);
    const formattedPrice = totalPrice.toLocaleString('ru-RU');

    // Get selected type name
    const typeName = typeSelect.options[typeSelect.selectedIndex].text;

    // Update display
    displayType.textContent = typeName;
    displayTotal.textContent = `${formattedPrice} ₽`;

    resultDiv.innerHTML = `
        <div style="text-align: center;">
            <p style="color: var(--muted-foreground); margin-bottom: 8px;">Стоимость потолка:</p>
            <p style="font-size: 2rem; font-weight: 700; color: var(--primary); margin-bottom: 4px;">${formattedPrice} ₽</p>
            <p style="font-size: 0.875rem; color: var(--muted-foreground);">
                *Точная стоимость рассчитывается после замера
            </p>
        </div>
    `;

    // Send goal to Yandex.Metrika
    if (typeof ym !== 'undefined') {
        ym(87509078, 'reachGoal', 'calculate_price');
    }
}

// Show/hide quantity input based on lighting selection
document.getElementById('lighting').addEventListener('change', function() {
    const quantityGroup = document.getElementById('quantity-group');
    const value = parseFloat(this.value);

    if (value === 600 || value === 550) {
        // Show quantity input for chandelier or spotlights
        quantityGroup.style.display = 'block';
    } else {
        quantityGroup.style.display = 'none';
    }
});

// Enter key in calculator
document.getElementById('area').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        e.preventDefault();
        calculatePrice();
    }
});

// Modal functions
function openModal(title = 'Заказать звонок', description = 'Оставьте свои контакты и мы свяжемся с вами в ближайшее время') {
    const modal = document.getElementById('modal');
    const modalTitle = document.getElementById('modal-title');
    const modalDescription = document.getElementById('modal-description');

    modalTitle.textContent = title;
    modalDescription.textContent = description;

    // Store calculator data if opening from calculator
    if (title === 'Заказать точный расчет') {
        const area = document.getElementById('area').value;
        const typeSelect = document.getElementById('type');
        const displayTotal = document.getElementById('display-total').textContent;

        if (area && typeSelect.value) {
            const calculatorData = {
                area: area,
                type: typeSelect.options[typeSelect.selectedIndex].text,
                total: displayTotal
            };
            modal.setAttribute('data-calculator', JSON.stringify(calculatorData));
        }
    }

    modal.classList.add('active');
    document.body.style.overflow = 'hidden';

    // Send goal to Yandex.Metrika
    if (typeof ym !== 'undefined') {
        ym(87509078, 'reachGoal', 'open_modal');
    }
}

function closeModal() {
    const modal = document.getElementById('modal');
    modal.classList.remove('active');
    modal.removeAttribute('data-calculator');
    document.body.style.overflow = '';
}

// Close modal on outside click
window.onclick = function(event) {
    const modal = document.getElementById('modal');
    if (event.target === modal) {
        closeModal();
    }
}

// Close modal on ESC key
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        closeModal();
    }
});

// Enable Enter key in modal form inputs
document.querySelectorAll('#modalForm input').forEach(input => {
    input.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            document.getElementById('modalForm').dispatchEvent(new Event('submit'));
        }
    });
});

// Modal form submission
document.getElementById('modalForm').addEventListener('submit', async function(e) {
    e.preventDefault();

    const name = document.getElementById('modal-name').value;
    const phone = document.getElementById('modal-phone').value;
    const modalTitle = document.getElementById('modal-title').textContent;
    const modal = document.getElementById('modal');

    const data = {
        form_type: 'modal',
        title: modalTitle,
        name: name,
        phone: phone,
        timestamp: new Date().toISOString(),
        page_url: window.location.href
    };

    // Add calculator data if exists
    const calculatorData = modal.getAttribute('data-calculator');
    if (calculatorData) {
        const calcData = JSON.parse(calculatorData);
        data.calculator_area = calcData.area;
        data.calculator_type = calcData.type;
        data.calculator_total = calcData.total;
    }

    try {
        console.log('Sending modal form data:', data);

        const response = await fetch(WEBHOOK_CONFIG.url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });

        console.log('Response status:', response.status);

        if (response.ok) {
            const responseData = await response.json();
            console.log('Response data:', responseData);

            showSuccess('Заявка отправлена!', 'Мы свяжемся с вами в ближайшее время.');

            // Send goal to Yandex.Metrika
            if (typeof ym !== 'undefined') {
                ym(87509078, 'reachGoal', 'submit_modal_form');
            }

            closeModal();
            this.reset();
        } else {
            throw new Error('Server error');
        }
    } catch (error) {
        console.error('Error sending form:', error);
        showError('Ошибка отправки', 'Пожалуйста, позвоните нам: +7 (900) 696-30-25');
    }
});

// Enable Enter key in contact form inputs (except textarea)
document.querySelectorAll('#contactForm input, #contactForm select').forEach(input => {
    input.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            document.getElementById('contactForm').dispatchEvent(new Event('submit'));
        }
    });
});

// Contact form submission
document.getElementById('contactForm').addEventListener('submit', async function(e) {
    e.preventDefault();

    const name = document.getElementById('name').value;
    const phone = document.getElementById('phone').value;
    const email = document.getElementById('email').value;
    const service = document.getElementById('service').value;
    const message = document.getElementById('message').value;

    const serviceNames = {
        'matte': 'Матовые потолки',
        'glossy': 'Глянцевые потолки',
        'satin': 'Сатиновые потолки',
        'printed': 'Потолки с печатью',
        'repair': 'Ремонт потолков'
    };

    const data = {
        form_type: 'contact',
        name: name,
        phone: phone,
        email: email || 'Не указан',
        service: service ? serviceNames[service] : 'Не выбрана',
        message: message || 'Нет сообщения',
        timestamp: new Date().toISOString(),
        page_url: window.location.href
    };

    try {
        console.log('Sending contact form data:', data);

        const response = await fetch(WEBHOOK_CONFIG.url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });

        console.log('Response status:', response.status);

        if (response.ok) {
            const responseData = await response.json();
            console.log('Response data:', responseData);

            showSuccess('Сообщение отправлено!', 'Мы свяжемся с вами в ближайшее время.');

            // Send goal to Yandex.Metrika
            if (typeof ym !== 'undefined') {
                ym(87509078, 'reachGoal', 'submit_contact_form');
            }

            this.reset();
        } else {
            throw new Error('Server error');
        }
    } catch (error) {
        console.error('Error sending form:', error);
        showError('Ошибка отправки', 'Пожалуйста, позвоните нам: +7 (900) 696-30-25');
    }
});

// Phone input mask
const phoneInputs = document.querySelectorAll('input[type="tel"]');
phoneInputs.forEach(input => {
    input.addEventListener('input', function(e) {
        let value = e.target.value.replace(/\D/g, '');
        let formattedValue = '';

        if (value.length > 0) {
            if (value[0] !== '7') {
                value = '7' + value;
            }
            formattedValue = '+7';
            if (value.length > 1) {
                formattedValue += ' (' + value.substring(1, 4);
            }
            if (value.length >= 5) {
                formattedValue += ') ' + value.substring(4, 7);
            }
            if (value.length >= 8) {
                formattedValue += '-' + value.substring(7, 9);
            }
            if (value.length >= 10) {
                formattedValue += '-' + value.substring(9, 11);
            }
        }

        e.target.value = formattedValue;
    });

    input.addEventListener('focus', function(e) {
        if (!e.target.value) {
            e.target.value = '+7 ';
        }
    });

    input.addEventListener('keydown', function(e) {
        if (e.key === 'Backspace' && e.target.value === '+7 ') {
            e.target.value = '';
        }
    });
});

// Intersection Observer for animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver(function(entries) {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Apply animation to elements
document.addEventListener('DOMContentLoaded', function() {
    const animatedElements = document.querySelectorAll(
        '.product-card, .gallery__item, .stat'
    );

    animatedElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });

    // Add stagger effect
    const productCards = document.querySelectorAll('.product-card');
    productCards.forEach((card, index) => {
        card.style.transitionDelay = `${index * 0.1}s`;
    });

    const galleryItems = document.querySelectorAll('.gallery__item');
    galleryItems.forEach((item, index) => {
        item.style.transitionDelay = `${index * 0.1}s`;
    });
});

console.log('Сайт успешно загружен! 🚀');
