document.addEventListener('DOMContentLoaded', function() {
    const nameInput = document.getElementById('name');
    const createBtn = document.getElementById('createBtn');
    const loadingModal = document.getElementById('loadingModal');
    const successModal = document.getElementById('successModal');
    const linkInput = document.getElementById('linkInput');
    const copyBtn = document.getElementById('copyBtn');
    const continueBtn = document.getElementById('continueBtn');

    let currentRoomId = null;

    // Focus input on load
    nameInput.focus();

    // Create chat room
    createBtn.addEventListener('click', createChatRoom);
    nameInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') createChatRoom();
    });

    async function createChatRoom() {
        const name = nameInput.value.trim();

        if (!name || name.length < 2) {
            alert('Nama harus minimal 2 karakter');
            nameInput.focus();
            return;
        }

        showLoading(true);

        try {
            const response = await fetch('/create-room', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ name: name })
            });

            const data = await response.json();

            if (!response.ok) {
                alert(data.error || 'Gagal membuat chat room');
                showLoading(false);
                return;
            }

            currentRoomId = data.room_id;
            const fullLink = window.location.origin + '/join/' + data.access_link;
            
            linkInput.value = fullLink;
            showSuccessModal(fullLink);

        } catch (error) {
            console.error('Error:', error);
            alert('Tidak dapat terhubung ke server');
            showLoading(false);
        }
    }

    function showLoading(show) {
        loadingModal.classList.toggle('hidden', !show);
    }

    function showSuccessModal(link) {
        showLoading(false);
        
        // Generate QR code
        const qrcodeContainer = document.getElementById('qrcode');
        qrcodeContainer.innerHTML = '';
        new QRCode(qrcodeContainer, {
            text: link,
            width: 200,
            height: 200,
            correctLevel: QRCode.CorrectLevel.H
        });

        successModal.classList.remove('hidden');
    }

    // Copy link to clipboard
    copyBtn.addEventListener('click', () => {
        linkInput.select();
        document.execCommand('copy');
        
        const originalText = copyBtn.textContent;
        copyBtn.textContent = 'Tersalin!';
        copyBtn.style.backgroundColor = 'var(--secondary-color)';
        
        setTimeout(() => {
            copyBtn.textContent = originalText;
            copyBtn.style.backgroundColor = '';
        }, 2000);
    });

    // Continue to chat
    continueBtn.addEventListener('click', () => {
        if (currentRoomId) {
            window.location.href = `/chat/${currentRoomId}`;
        }
    });
});
