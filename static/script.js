document.addEventListener('DOMContentLoaded', function() {
    const searchBar = document.getElementById('search-bar');
    const searchResults = document.getElementById('search-results');

    const services = [
        "AC Repair",
        "AC Fitting & Installation",
        "AC Servicing",
        "Plumbing",
        "Pipe fitting",
        "Tap and Faucet Repair",
        "Electrician",
        "Wiring and Rewiring",
        "Switch and Socket Repair",
        "Fan Installation",
        "Carpentry",
        "Furniture Repair",
        "Door and Window Repair",
        "Painting",
        "Interior and Exterior Painting",
        "Wallpapers",
        "Cleaning",
        "Deep Home Cleaning",
        "Sofa Cleaning",
        "Bathroom Cleaning",
        "Pest Control",
        "Cockroach and Ant Control",
        "Bed Bugs Control",
        "Termite Control",
        "Home Appliances Repair",
        "Washing Machine Repair",
        "Refrigerator Repair",
        "Microwave and Oven Repair",
        "Water Purifier Repair",
        "Geyser Repair",
        "Home Salon",
        "Haircut and Styling",
        "Manicure and Pedicure",
        "Facial and Skincare",
        "Massage Therapy"
    ];

    searchBar.addEventListener('input', function() {
        const inputText = searchBar.value.toLowerCase();
        if (inputText.length === 0) {
            searchResults.innerHTML = '';
            searchResults.style.display = 'none';
            return;
        }

        const filteredServices = services.filter(service => 
            service.toLowerCase().includes(inputText)
        );

        if (filteredServices.length > 0) {
            searchResults.innerHTML = filteredServices.map(service => 
                `<a href="/result?service=${encodeURIComponent(service)}">${service}</a>`
            ).join('');
            searchResults.style.display = 'block';
        } else {
            searchResults.style.display = 'none';
        }
    });

    document.addEventListener('click', function(e) {
        if (e.target.id !== 'search-bar') {
            searchResults.style.display = 'none';
        }
    });

    function showToast(message, type = 'success') {
        const toastContainer = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        toastContainer.appendChild(toast);

        setTimeout(() => {
            toast.classList.add('show');
        }, 100);

        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => {
                toast.remove();
            }, 300);
        }, 3000);
    }

    // Example of how to use the toast notification
    // showToast('Successfully logged in!', 'success');
    // showToast('Invalid credentials!', 'error');
});
