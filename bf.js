function brainfuck(source, stdin, stdout) {
  'use strict';
  var memory = [];
  var i = 0;
  var insPtr = 0;
  var polling = false;

  if (stdout === undefined) {
    stdin = document;
  }
  if (stdout === undefined) {
    stdout = document;
  }
  var tokens  = {
    '>': function incrementPtr() {
      i++;
    },
    '<': function decrementPtr() {
      i--;
    },
    '+': function incrementValue() {
      if (memory[i] === undefined) {
        memory[i] = 0;
      }
      memory[i]++;
    },
    '-': function decrementValue() {
      if (memory[i] === undefined) {
        memory[i] = 0;
      }
      memory[i]--;
    },
    '.': function printValue() {
      if ('value' in stdout) {
        stdout.value = stdout.value + String.fromCharCode(memory[i]);
      } else if ('innerText' in stdout) {
        stdout.innerText = stdout.innerText + String.fromCharCode(memory[i]);
      } else {
        document.write(String.fromCharCode(memory[i]));
      }
    },
    ',': function getValue() {
      polling = true;
      if ('value' in stdin) {
        stdin.focus();
      }
      stdin.onkeypress = function (e) {
        memory[i] = e.charCode;
        polling = false;
        document.onkeypress = null;
      };
    },
    '[': function jumpForwardIfZero() {
      if (memory[i] === 0) {
        insPtr += source.substr(insPtr).indexOf(']');
      }
    },
    ']': function jumpBackwardIfNotZero() {
      if (memory[i] !== 0) {
        insPtr = source.substr(0, insPtr).lastIndexOf('[');
      }
    }
  };
  var step = function () {
    if (insPtr > source.length) return;
    if (polling) {
      setTimeout(step, 500);
      return;
    }
    if (source[insPtr] in tokens) {
      tokens[source[insPtr]]();
    }
    insPtr++;
    step();
  }
  step();
}

document.onreadystatechange = function() {
  'use strict';
  if (document.readyState === "complete") {
    var inEl = document.getElementById('stdin');
    var outEl = document.getElementById('stdout');
    var sourceEl = document.getElementById('source');
    var runEl = document.getElementsByClassName('js-run')[0];
    var resetEl = document.getElementsByClassName('js-reset')[0];
    
    runEl.onclick = function () {
      brainfuck(sourceEl.value, inEl, outEl);
    };
    resetEl.onclick = function () {
      sourceEl.value = '';
      inEl.value = inEl.value + '\n';
      outEl.value = outEl.value + '\n';
    };
  }
}
