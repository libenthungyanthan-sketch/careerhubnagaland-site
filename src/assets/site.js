// Career Hub Nagaland: enquiry form helpers. The site works without this file.
(function () {
  var form = document.querySelector('form[action="/enquire.php"]');
  if (!form) return;

  var params = new URLSearchParams(location.search);
  var service = form.querySelector('#service');
  var whoInputs = form.querySelectorAll('input[name="who"]');

  // Pre-select from links such as /enquire/?service=assessment or ?type=school
  if (params.get('type') === 'school') {
    form.querySelector('input[name="who"][value="school"]').checked = true;
    service.value = 'school';
  }
  var s = params.get('service');
  if (s && service.querySelector('option[value="' + s.replace(/[^a-z0-9-]/g, '') + '"]')) {
    service.value = s;
    if (['graduate-call', 'clarity', 'readiness', 'architect'].indexOf(s) > -1) {
      form.querySelector('input[name="who"][value="graduate"]').checked = true;
    }
  }

  // Show only the fields that match "I am a"
  var conditional = {
    'class': ['parent', 'student18'],
    'concern': ['parent', 'student18', 'graduate'],
    'school_name': ['school']
  };
  function who() {
    var c = form.querySelector('input[name="who"]:checked');
    return c ? c.value : 'parent';
  }
  function update() {
    var w = who();
    form.querySelectorAll('[data-for]').forEach(function (el) {
      el.hidden = el.getAttribute('data-for').split(' ').indexOf(w) === -1;
    });
    Object.keys(conditional).forEach(function (id) {
      var el = form.querySelector('#' + id);
      if (el) el.required = conditional[id].indexOf(w) > -1;
    });
  }
  whoInputs.forEach(function (i) { i.addEventListener('change', update); });
  update();

  // Timestamp for simple bot filtering
  var t = document.createElement('input');
  t.type = 'hidden'; t.name = 't'; t.value = String(Date.now());
  form.appendChild(t);

  // Validation with a clear message next to the first problem
  form.addEventListener('submit', function (e) {
    var old = form.querySelector('.form-error');
    if (old) old.remove();
    var bad = Array.prototype.find.call(form.elements, function (el) {
      return el.willValidate && !el.closest('[hidden]') && !el.checkValidity();
    });
    if (bad) {
      e.preventDefault();
      var msg = document.createElement('p');
      msg.className = 'form-error';
      msg.setAttribute('role', 'alert');
      msg.style.color = '#8c3f10';
      msg.style.fontWeight = '700';
      var label = bad.type === 'checkbox' ? 'Please tick the consent box to send your enquiry.' :
        'Please complete: ' + ((form.querySelector('label[for="' + bad.id + '"]') || {}).textContent || 'this field').replace('*', '').trim() + '.';
      msg.textContent = label;
      (bad.closest('.field') || bad).after(msg);
      bad.focus();
    }
  });
})();
