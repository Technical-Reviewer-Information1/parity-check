(function () {
  'use strict';
  const T = window.Tools, $ = id => document.getElementById(id);
  const shuffle = a => { a = a.slice(); for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; };
  const ones = a => a.reduce((x, y) => x + y, 0);

  let even = true;                       // true＝偶数パリティ
  let data = [1, 0, 1, 1, 0, 1, 1];      // 7ビット
  let answered = false;

  function parityOf(bits) {
    const c = ones(bits);
    return even ? (c % 2 === 0 ? 0 : 1) : (c % 2 === 0 ? 1 : 0);
  }

  /* ---------- STEP1 ---------- */
  function drawBits1() {
    const box = $('bits1'); box.innerHTML = '';
    data.forEach((v, i) => {
      const b = document.createElement('button');
      b.className = 'bit' + (v ? ' on' : '');
      b.textContent = v;
      b.addEventListener('click', () => { data[i] = 1 - data[i]; answered = false; $('pFb').hidden = true; drawAll(); });
      box.appendChild(b);
    });
    const p = document.createElement('button');
    p.className = 'bit par' + (answered && parityOf(data) ? ' on' : '');
    p.textContent = answered ? parityOf(data) : '?';
    p.disabled = true;
    box.appendChild(p);
    const c = ones(data);
    $('cnt1').innerHTML = 'いまの7ビットに含まれる「1」の個数 ＝ <strong>' + c + ' 個</strong>（' +
      (c % 2 === 0 ? '偶数' : '奇数') + '）';
    $('modeDesc').innerHTML = even
      ? '<strong>偶数パリティ</strong>：パリティビットを含めた全体の「1」の個数が<strong>偶数</strong>になるようにします。'
      : '<strong>奇数パリティ</strong>：パリティビットを含めた全体の「1」の個数が<strong>奇数</strong>になるようにします。';
    document.getElementById('modeEven').setAttribute('aria-pressed', even);
    document.getElementById('modeOdd').setAttribute('aria-pressed', !even);
  }
  function answerParity(v) {
    const ans = parityOf(data);
    answered = true;
    const fb = $('pFb'); fb.hidden = false;
    const ok = v === ans;
    fb.className = 'note ' + (ok ? 'ok' : 'ng');
    const c = ones(data);
    fb.innerHTML = (ok ? '正解。' : '正解は <strong>' + ans + '</strong>。') +
      '7ビットの1の個数は ' + c + ' 個（' + (c % 2 === 0 ? '偶数' : '奇数') + '）。' +
      (even
        ? '偶数パリティなので、全体を偶数にするには ' + (c % 2 === 0 ? '<strong>0</strong> を足します（そのままで偶数）。' : '<strong>1</strong> を足します。')
        : '奇数パリティなので、全体を奇数にするには ' + (c % 2 === 0 ? '<strong>1</strong> を足します。' : '<strong>0</strong> を足します（そのままで奇数）。')) +
      '<br>送るビット列は <span class="mono">' + data.join('') + ans + '</span> です。';
    drawAll();
  }

  /* ---------- STEP2 ---------- */
  let recv = [], flipped = [];
  function resetRecv() {
    recv = data.concat([parityOf(data)]);
    flipped = [];
    drawBits2();
  }
  function drawBits2() {
    const box = $('bits2'); box.innerHTML = '';
    recv.forEach((v, i) => {
      const b = document.createElement('button');
      b.className = 'bit' + (v ? ' on' : '') + (i === 7 ? ' par' : '') + (flipped.indexOf(i) >= 0 ? ' flip' : '');
      b.textContent = v;
      b.addEventListener('click', () => {
        recv[i] = 1 - recv[i];
        const k = flipped.indexOf(i);
        if (k >= 0) flipped.splice(k, 1); else flipped.push(i);
        drawBits2();
      });
      box.appendChild(b);
    });
    const c = ones(recv);
    const okParity = even ? (c % 2 === 0) : (c % 2 === 1);
    $('cnt2').innerHTML = '受け取った8ビットの「1」の個数 ＝ <strong>' + c + ' 個</strong>（' +
      (c % 2 === 0 ? '偶数' : '奇数') + '）';
    const n = $('checkNote');
    if (!flipped.length) {
      n.className = 'note ok';
      n.innerHTML = '<strong>誤りは検出されませんでした。</strong>1の個数が' + (even ? '偶数' : '奇数') +
        'なので、正しく届いたと判断します。ビットをクリックして反転させてみましょう。';
    } else if (!okParity) {
      n.className = 'note ng';
      n.innerHTML = '<strong>誤りを検出しました。</strong>1の個数が' + (even ? '偶数' : '奇数') +
        'になっていません（' + flipped.length + ' ビット反転しています）。<br>' +
        'ただし<strong>どのビットが誤ったかはわかりません</strong>。再送してもらうことになります。';
    } else {
      n.className = 'note warn';
      n.innerHTML = '<strong>誤りが ' + flipped.length + ' 個あるのに、検出できませんでした。</strong>' +
        '偶数個の誤りでは1の個数の偶奇が元にもどってしまうためです。<strong>これがパリティチェックの限界</strong>です。';
    }
  }
  function flipN(n) {
    resetRecv();
    const idx = shuffle([0, 1, 2, 3, 4, 5, 6, 7]).slice(0, n);
    idx.forEach(i => { recv[i] = 1 - recv[i]; flipped.push(i); });
    drawBits2();
  }

  /* ---------- STEP3 水平垂直パリティ ---------- */
  let g = [[1, 0, 1, 1], [0, 1, 1, 0], [1, 1, 0, 1], [0, 0, 1, 1]];
  let gErr = null, gShow = false;
  function fullGrid() {
    const out = g.map(row => row.concat([row.reduce((a, b) => a ^ b, 0)]));
    const last = [];
    for (let j = 0; j < 5; j++) last.push(out.reduce((a, r) => a ^ r[j], 0));
    return out.concat([last]);
  }
  function drawGrid() {
    const f = fullGrid();
    if (gErr) f[gErr[0]][gErr[1]] = 1 - f[gErr[0]][gErr[1]];
    const box = $('grid44'); box.innerHTML = '';
    // 誤り位置の判定
    let badRow = -1, badCol = -1;
    for (let i = 0; i < 5; i++) if (f[i].reduce((a, b) => a ^ b, 0) !== 0) badRow = i;
    for (let j = 0; j < 5; j++) { let x = 0; for (let i = 0; i < 5; i++) x ^= f[i][j]; if (x !== 0) badCol = j; }
    for (let i = 0; i < 5; i++) for (let j = 0; j < 5; j++) {
      const d = document.createElement('div');
      const isPar = (i === 4 || j === 4);
      d.className = 'c' + (f[i][j] ? ' on' : '') + (isPar ? ' par' : '') +
        (gShow && i === badRow && j === badCol ? ' hit' : '');
      d.textContent = f[i][j];
      d.addEventListener('click', () => {
        if (i < 4 && j < 4) { g[i][j] = 1 - g[i][j]; gErr = null; gShow = false; drawGrid(); }
      });
      box.appendChild(d);
    }
    const n = $('gridNote');
    if (!gErr) {
      n.className = 'note ok';
      n.innerHTML = '<strong>行も列も、1の個数がすべて偶数</strong>になっています。誤りはありません。' +
        '（左上4×4のマスをクリックするとデータを変えられます。）';
    } else if (!gShow) {
      n.className = 'note warn';
      n.innerHTML = '誤りを1つ起こしました。<strong>どの行・どの列のパリティが合わなくなったか</strong>を探してみましょう。' +
        '「誤りの位置を調べる」を押すと答えが出ます。';
    } else {
      n.className = 'note ok';
      n.innerHTML = '<strong>' + (badRow + 1) + ' 行 ' + (badCol + 1) + ' 列目</strong>が誤りです。正しくは <strong>' +
        (1 - f[badRow][badCol]) + '</strong>。<br>' +
        '行のパリティが合わない行と、列のパリティが合わない列の<strong>交わったところ</strong>が誤りの位置です。' +
        'これなら<strong>位置を特定して訂正までできます</strong>。';
    }
  }

  /* ---------- STEP4 クイズ ---------- */
  const QUIZ = [
    { t: '「0111011」に奇数パリティを追加するとどうなるか。',
      choices: ['01110110', '01110111', '00111011', '10111011'], a: '01110110',
      why: '0111011 の1の個数は5個（奇数）。奇数パリティは全体を奇数にするので、<strong>0</strong>を末尾に足して 01110110 になります。' },
    { t: '「1011011」に偶数パリティを追加するとどうなるか。',
      choices: ['10110111', '10110110', '01011011', '11011011'], a: '10110111',
      why: '1011011 の1の個数は5個（奇数）。偶数パリティは全体を偶数にするので、<strong>1</strong>を足して6個にします。' },
    { t: 'パリティチェックについて正しいものはどれか。',
      choices: ['誤りが奇数個の場合のみ検出できる', 'どのビットが誤ったか特定できる',
                '検出した誤りを訂正できる', '誤りが偶数個の場合のみ検出できる'],
      a: '誤りが奇数個の場合のみ検出できる',
      why: '偶数個の誤りでは1の個数の偶奇が元にもどるため気づけません。位置の特定も訂正もできません。' },
    { t: '偶数パリティで受け取った8ビットの1の個数が7個だった。どう判断するか。',
      choices: ['誤りがある', '誤りはない', '誤りが2個ある', '判断できない'], a: '誤りがある',
      why: '偶数パリティなら1の個数は偶数のはずです。7個（奇数）なので、奇数個の誤りが起きています。' },
    { t: '行と列の両方にパリティを付けると何ができるようになるか。',
      choices: ['誤りが1個なら位置を特定して訂正できる', '誤りが何個あっても訂正できる',
                '誤りを防げる', '通信速度が上がる'],
      a: '誤りが1個なら位置を特定して訂正できる',
      why: '合わない行と合わない列の交点が誤りの位置です。ただし2個以上の誤りには対応できません。' },
    { t: 'パリティビットを付ける目的はどれか。',
      choices: ['受信したデータに誤りがないか確認するため', 'データを小さくするため',
                'データを暗号化するため', '通信を速くするため'],
      a: '受信したデータに誤りがないか確認するため',
      why: '誤り検出のための工夫です。データ量はむしろ増えます。' }
  ];
  let qList = [], qi = 0, qScore = 0;
  function startQuiz() { qList = shuffle(QUIZ); qi = 0; qScore = 0; renderQ(); }
  function renderQ() {
    if (qi >= qList.length) {
      $('qText').textContent = qScore + ' / ' + qList.length + ' 問正解';
      $('qChoices').innerHTML = ''; $('qFb').hidden = true; $('qNext').disabled = true;
      $('qProgress').textContent = qList.length + ' / ' + qList.length; return;
    }
    const it = qList[qi];
    $('qProgress').textContent = (qi + 1) + ' / ' + qList.length;
    $('qScore').textContent = qScore;
    $('qText').textContent = it.t;
    const box = $('qChoices'); box.className = 'choice4'; box.innerHTML = '';
    shuffle(it.choices).forEach(c => {
      const b = document.createElement('button');
      b.className = 'btn'; b.textContent = c; b.dataset.c = c; b.style.textAlign = 'center';
      b.addEventListener('click', () => answerQ(c));
      box.appendChild(b);
    });
    $('qFb').hidden = true; $('qNext').disabled = true;
    $('qNext').textContent = (qi === qList.length - 1) ? '結果を見る' : '次の問題';
  }
  function answerQ(c) {
    const it = qList[qi], ok = c === it.a, box = $('qChoices');
    box.classList.add('locked');
    [...box.children].forEach(b => {
      if (b.dataset.c === it.a) b.classList.add('correct');
      else if (b.dataset.c === c) b.classList.add('wrong');
    });
    if (ok) qScore++;
    const fb = $('qFb');
    fb.className = 'note ' + (ok ? 'ok' : 'ng');
    fb.innerHTML = (ok ? '正解。' : '正解は「<strong>' + it.a + '</strong>」。') + it.why;
    fb.hidden = false;
    $('qScore').textContent = qScore; $('qNext').disabled = false;
  }

  function drawAll() { drawBits1(); resetRecv(); }

  function init() {
    $('modeEven').addEventListener('click', () => { even = true; answered = false; $('pFb').hidden = true; drawAll(); });
    $('modeOdd').addEventListener('click', () => { even = false; answered = false; $('pFb').hidden = true; drawAll(); });
    document.querySelectorAll('[data-p]').forEach(b => b.addEventListener('click', () => answerParity(+b.dataset.p)));
    document.querySelectorAll('[data-set]').forEach(b => b.addEventListener('click', () => {
      data = b.dataset.set.split('').map(Number); answered = false; $('pFb').hidden = true; drawAll();
    }));
    $('randBits').addEventListener('click', () => {
      data = Array.from({ length: 7 }, () => Math.random() < .5 ? 1 : 0);
      answered = false; $('pFb').hidden = true; drawAll();
    });
    $('flip1').addEventListener('click', () => flipN(1));
    $('flip2').addEventListener('click', () => flipN(2));
    $('restore2').addEventListener('click', resetRecv);
    $('makeErr').addEventListener('click', () => {
      gErr = [Math.floor(Math.random() * 5), Math.floor(Math.random() * 5)];
      gShow = false; drawGrid();
    });
    $('findErr').addEventListener('click', () => { if (gErr) { gShow = true; drawGrid(); } });
    $('resetGrid').addEventListener('click', () => { gErr = null; gShow = false; drawGrid(); });
    $('qNext').addEventListener('click', () => { qi++; renderQ(); });
    $('qReset').addEventListener('click', startQuiz);
    window.Terms.glossary($('glossBox'), ['パリティチェック', 'パリティビット', '誤り検出', 'パケット', 'プロトコル']);
    drawAll(); drawGrid(); startQuiz();
    window.Terms.attach();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
