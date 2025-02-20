
async function loadBlockedCards() {
    const response = await fetch('/admin/blocked-cards');
    const cards = await response.json();
    const tableBody = document.querySelector('#blockedCardsTable tbody');
  
    tableBody.innerHTML = '';
  

    cards.forEach(card => {
      const row = document.createElement('tr');
      row.innerHTML = `
        <td>${card.cardNumber}</td>
        <td>${card.reason}</td>
        <td><button onclick="unblockCard('${card.cardNumber}')">Unblock</button></td>
      `;
      tableBody.appendChild(row);
    });
  }
  
  async function unblockCard(cardNumber) {
    const response = await fetch('/admin/unblock-card', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ cardNumber })
    });
  
    const result = await response.json();
    alert(result.message);
    loadBlockedCards();  
  }
  
  
  window.onload = loadBlockedCards;
  