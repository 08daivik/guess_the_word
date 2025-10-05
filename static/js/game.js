let currentGameId = null;

document.addEventListener('DOMContentLoaded', () => {
  const startBtn = document.getElementById('start-btn');
  const guessForm = document.getElementById('guess-form');
  const guessInput = document.getElementById('guess-input');
  const submitBtn = document.getElementById('submit-guess');
  const messages = document.getElementById('messages');
  const guessesDiv = document.getElementById('guesses');

  // 🎮 Start a new game
  startBtn?.addEventListener('click', async () => {
    const res = await fetch('/play/start', { method: 'POST' });
    const data = await res.json();

    if (!res.ok) {
      messages.innerText = data.msg || 'Could not start';
      return;
    }

    currentGameId = data.game_id;
    messages.innerText = 'Game started. You have 5 guesses.';
    guessForm.style.display = 'block';
    guessesDiv.innerHTML = '';
    guessInput.value = '';
    guessInput.focus();
  });

  // 💬 Submit a guess
  submitBtn?.addEventListener('click', async () => {
    const guess = guessInput.value.trim().toUpperCase();

    if (!guess || guess.length !== 5) {
      alert('Enter a 5-letter word');
      return;
    }

    const res = await fetch('/play/guess', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ game_id: currentGameId, guess })
    });

    const data = await res.json();

    if (!res.ok) {
      alert(data.msg || 'Error');
      return;
    }

    // 🧱 Render guess feedback
    const fb = data.feedback; // e.g. ['green','grey','orange','grey','green']
    const row = document.createElement('div');
    row.classList.add('guess-row');
    row.style.display = 'flex';
    row.style.gap = '8px';
    row.style.marginTop = '10px';
    row.style.justifyContent = 'center';

    fb.forEach((ch, i) => {
      const el = document.createElement('div');
      el.style.width = '50px';
      el.style.height = '50px';
      el.style.display = 'flex';
      el.style.alignItems = 'center';
      el.style.justifyContent = 'center';
      el.style.fontWeight = '700';
      el.style.fontSize = '20px';
      el.style.borderRadius = '6px';
      el.style.color = '#fff';
      el.textContent = guess[i]; // ✅ FIXED — use index `i`

      // 🎨 Color feedback
      if (ch === 'green') el.style.background = '#22c55e';
      else if (ch === 'orange') el.style.background = '#f97316';
      else el.style.background = '#6b7280';

      // ✨ Add animation
      el.style.transition = 'transform 0.2s ease, background 0.3s ease';
      el.style.transform = 'scale(0.9)';
      setTimeout(() => { el.style.transform = 'scale(1)'; }, 100 * i);

      row.appendChild(el);
    });

    guessesDiv.appendChild(row);
    guessInput.value = '';
    guessInput.focus();

    // 🏁 Check status
    if (data.status === 'won') {
      messages.innerText = '🎉 Congrats! You won the game!';
      guessForm.style.display = 'none';
    } else if (data.status === 'lost') {
      messages.innerText = '😢 Game over! Better luck next time.';
      guessForm.style.display = 'none';
    } else {
      messages.innerText = `Guesses used: ${data.guesses_used}/5`;
    }
  });
});
