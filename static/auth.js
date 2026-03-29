// --- SIGN UP SECTION ---
const signupForm = document.getElementById('signupForm');
if (signupForm) {
    signupForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        const name = document.getElementById('name').value;
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;

        try {
            const response = await fetch('/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, email, password })
            });
            const result = await response.json();
            if (response.ok) {
                alert("Account created successfully!");
                window.location.href = '/login_page';
            } else {
                alert(result.message);
            }
        } catch (error) {
            console.error("Signup error:", error);
        }
    });
}

// --- LOGIN SECTION ---
const loginForm = document.getElementById('loginForm');
if (loginForm) {
    loginForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        const email = document.getElementById('loginEmail').value;
        const password = document.getElementById('loginPassword').value;

        try {
            const response = await fetch('/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });
            const result = await response.json();
            if (response.ok) {
                alert("Login successful!");
                window.location.href = '/'; 
            } else {
                alert(result.message);
            }
        } catch (error) {
            console.error("Login error:", error);
            alert("Could not connect to server.");
        }
    });
}