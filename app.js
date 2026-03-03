// Shopping Cart Management
let cart = [];

// Add to cart functionality
document.querySelectorAll('.add-to-cart').forEach(button => {
    button.addEventListener('click', function() {
        const product = this.getAttribute('data-product');
        const price = parseFloat(this.getAttribute('data-price'));
        const productName = this.closest('.tier').querySelector('h4').textContent;
        
        const cartItem = {
            id: product,
            name: productName,
            price: price,
            quantity: 1
        };
        
        // Check if item already in cart
        const existingItem = cart.find(item => item.id === product);
        if (existingItem) {
            existingItem.quantity++;
        } else {
            cart.push(cartItem);
        }
        
        updateCart();
        showCart();
    });
});

// Update cart display
function updateCart() {
    const cartItemsDiv = document.getElementById('cart-items');
    const totalPriceSpan = document.getElementById('total-price');
    
    cartItemsDiv.innerHTML = '';
    let total = 0;
    
    cart.forEach(item => {
        const itemDiv = document.createElement('div');
        itemDiv.className = 'cart-item';
        itemDiv.innerHTML = `
            <div>
                <strong>${item.name}</strong> x${item.quantity}
                <br>₪${(item.price * item.quantity).toLocaleString('he-IL')}
                <button class="remove-item" data-id="${item.id}">הסר</button>
            </div>
        `;
        cartItemsDiv.appendChild(itemDiv);
        total += item.price * item.quantity;
    });
    
    totalPriceSpan.textContent = `₪${total.toLocaleString('he-IL')}`;
    
    // Add remove functionality
    document.querySelectorAll('.remove-item').forEach(btn => {
        btn.addEventListener('click', function() {
            const id = this.getAttribute('data-id');
            cart = cart.filter(item => item.id !== id);
            updateCart();
        });
    });
}

// Show/hide cart
function showCart() {
    if (cart.length > 0) {
        document.getElementById('cart').classList.add('active');
    }
}

// Checkout with Payoneer
document.getElementById('checkout-btn').addEventListener('click', function() {
    if (cart.length === 0) {
        alert('סל הקניות ריק');
        return;
    }
    
    // Calculate total
    let total = 0;
    cart.forEach(item => {
        total += item.price * item.quantity;
    });
    
    // Create Payoneer checkout form
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = 'https://www.payoneer.com/checkout';
    
    // Add hidden fields for Payoneer
    const fields = {
        'merchant_id': 'YOUR_PAYONEER_MERCHANT_ID', // Will be replaced with actual ID
        'amount': total,
        'currency': 'ILS',
        'reference_id': 'CLARVIX_' + Date.now(),
        'customer_email': prompt('אנא הזן את כתובת האימייל שלך:'),
        'return_url': window.location.href,
        'cancel_url': window.location.href,
        'notify_url': 'https://your-domain.com/webhook/payoneer'
    };
    
    for (let key in fields) {
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = key;
        input.value = fields[key];
        form.appendChild(input);
    }
    
    // Add cart items to form
    cart.forEach((item, index) => {
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = `item_${index + 1}`;
        input.value = `${item.name} x${item.quantity} - ₪${item.price * item.quantity}`;
        form.appendChild(input);
    });
    
    document.body.appendChild(form);
    form.submit();
});

// Contact form
document.getElementById('contact-form').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const email = this.querySelector('input[type="email"]').value;
    const name = this.querySelector('input[type="text"]').value;
    const message = this.querySelector('textarea').value;
    
    // Send to email service (e.g., EmailJS, Formspree, etc.)
    console.log('Contact form submitted:', { email, name, message });
    
    // For now, just show a success message
    alert('תודה על הפנייה שלך! נחזור אליך בקרוב.');
    this.reset();
});

// CTA button
document.querySelector('.cta-button').addEventListener('click', function() {
    document.getElementById('services').scrollIntoView({ behavior: 'smooth' });
});
