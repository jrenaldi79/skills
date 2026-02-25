/**
 * Google Messages Web - Utility Script
 * For use with Claude in Chrome on messages.google.com/web
 *
 * Functions:
 *   listConversations(limit)                    - List all visible conversations (for name lookup)
 *   checkNewMessages()                          - List all unread conversations
 *   navigateToConversation("Name")              - Click into a conversation (returns immediately)
 *   extractMessages(limit)                      - Read messages from the currently open conversation
 *   sendMessage("Name", "text")                 - Send a message to an existing conversation (async)
 *   startNewMessage("+1...", "text")            - Start a brand new conversation (async)
 *   bulkFetchThreads(options)                   - Fetch full threads from multiple conversations (async)
 *
 * Reading workflow:
 *   1. Call navigateToConversation("Ross") → returns { status, name } immediately
 *   2. Wait 3 seconds for the conversation to load
 *   3. Call extractMessages(40) → returns [{ from, text, timestamp }] directly as a return value
 *   No console.log reading needed — extractMessages returns structured data.
 */


// ─────────────────────────────────────────────
// INTERNAL HELPER: find all matching conversations
// ─────────────────────────────────────────────
function _findMatches(query) {
  var items = document.querySelectorAll('mws-conversation-list-item');
  var matches = [];
  var q = query.toLowerCase();

  items.forEach(function(item) {
    var nameEl = item.querySelector('.name');
    var name = nameEl ? nameEl.textContent.trim().replace(/^Muted\s+/i, '') : '';
    if (!name) {
      var lines = item.innerText.split('\n').filter(function(l) { return l.trim(); });
      name = lines[0] || '';
    }
    if (name.toLowerCase().includes(q)) {
      matches.push({ name: name, item: item });
    }
  });

  return matches;
}


// ─────────────────────────────────────────────
// 0. LIST ALL VISIBLE CONVERSATIONS
// Returns structured array directly.
// ─────────────────────────────────────────────
function listConversations(limit) {
  limit = limit || 30;
  var items = document.querySelectorAll('mws-conversation-list-item');
  var results = [];

  Array.from(items).slice(0, limit).forEach(function(item) {
    var nameEl = item.querySelector('.name');
    var name = nameEl ? nameEl.textContent.trim().replace(/^Muted\s+/i, '') : '';
    var snippetEl = item.querySelector('mws-conversation-snippet');
    var snippet = snippetEl ? snippetEl.textContent.trim() : '';
    if (!name) {
      var lines = item.innerText.split('\n').filter(function(l) { return l.trim(); });
      name = lines[0] || 'Unknown';
      if (!snippet) snippet = lines[1] || '';
    }
    var timeEl = item.querySelector('mws-relative-timestamp');
    if (!timeEl) timeEl = item.querySelector('.list-item-info');
    var isUnread = !!item.querySelector('.text-content.unread');
    results.push({
      name: name,
      snippet: snippet,
      time: timeEl ? timeEl.textContent.trim() : '',
      unread: isUnread
    });
  });

  return results;
}


// ─────────────────────────────────────────────
// 1. CHECK FOR NEW (UNREAD) MESSAGES
// Returns structured array directly.
// ─────────────────────────────────────────────
function checkNewMessages() {
  var items = document.querySelectorAll('mws-conversation-list-item');
  var unread = [];

  items.forEach(function(item) {
    if (item.querySelector('.text-content.unread')) {
      var nameEl = item.querySelector('.name');
      var name = nameEl ? nameEl.textContent.trim().replace(/^Muted\s+/i, '') : '';
      var snippetEl = item.querySelector('mws-conversation-snippet');
      var snippet = snippetEl ? snippetEl.textContent.trim() : '';
      if (!name) {
        var lines = item.innerText.split('\n').filter(function(l) { return l.trim(); });
        name = lines[0] || 'Unknown';
        if (!snippet) snippet = lines[1] || '';
      }
      var timeEl = item.querySelector('mws-relative-timestamp');
      if (!timeEl) timeEl = item.querySelector('.list-item-info');
      unread.push({
        name: name,
        snippet: snippet,
        time: timeEl ? timeEl.textContent.trim() : ''
      });
    }
  });

  return unread;
}


// ─────────────────────────────────────────────
// 2a. NAVIGATE TO A CONVERSATION (step 1 of reading)
// Clicks into the conversation and returns immediately.
// Returns { status, name, matchCount } — no setTimeout.
// After calling this, wait 3 seconds, then call extractMessages().
// ─────────────────────────────────────────────
function navigateToConversation(name) {
  var matches = _findMatches(name);

  if (matches.length === 0) {
    return { status: 'error', error: 'No conversation found for: "' + name + '"', matchCount: 0 };
  }

  if (matches.length > 1) {
    return {
      status: 'ambiguous',
      error: 'Multiple conversations match "' + name + '"',
      matches: matches.map(function(m) { return m.name; }),
      matchCount: matches.length
    };
  }

  var found = matches[0];
  var link = found.item.querySelector('a');
  if (link) link.click();

  return { status: 'ok', name: found.name, matchCount: 1 };
}


// ─────────────────────────────────────────────
// 2b. EXTRACT MESSAGES (step 2 of reading)
// Reads the currently loaded conversation from the DOM.
// Returns a structured array — no console.log, no setTimeout.
// Call this AFTER navigateToConversation + a 3 second wait.
//
// Each message: { from, text, timestamp, isOutgoing }
// Timestamps come from date separators and per-message times.
// ─────────────────────────────────────────────
function extractMessages(limit) {
  limit = limit || 40;

  // Determine the conversation partner's name from the header
  var headerEl = document.querySelector('.title-container .title h2') ||
                 document.querySelector('div.title h2') ||
                 document.querySelector('[data-e2e-conversation-name]');
  var partnerName = headerEl ? headerEl.innerText.trim() : 'Them';

  // Fallback: try scanning for a non-sidebar h2
  if (partnerName === 'Them') {
    var allH2 = document.querySelectorAll('h2');
    for (var hi = 0; hi < allH2.length; hi++) {
      if (!allH2[hi].classList.contains('name') && allH2[hi].textContent.trim().length > 0 && allH2[hi].textContent.trim().length < 60) {
        partnerName = allH2[hi].textContent.trim();
        break;
      }
    }
  }

  var wrappers = document.querySelectorAll('mws-message-wrapper');
  if (wrappers.length === 0) {
    return { status: 'empty', messages: [], partnerName: partnerName };
  }

  var messages = [];
  var currentDateLabel = '';

  // Walk through ALL wrappers to track date labels, then slice at the end
  Array.from(wrappers).forEach(function(wrapper) {
    // Check for a date separator above this message
    var prev = wrapper.previousElementSibling;
    while (prev) {
      // Date separators are typically in elements like mws-relative-timestamp or .date-separator
      if (prev.classList && (prev.classList.contains('date-separator') ||
          prev.tagName === 'MWS-RELATIVE-TIMESTAMP' ||
          prev.classList.contains('separator'))) {
        currentDateLabel = prev.innerText.trim();
        break;
      }
      // Also check for timestamp in the parent structure
      if (prev.tagName === 'MWS-MESSAGE-WRAPPER') break; // stop at previous message
      prev = prev.previousElementSibling;
    }

    var isOutgoing = wrapper.getAttribute('is-outgoing') === 'true';

    // Try to get per-message timestamp
    var msgTime = '';
    var timeEl = wrapper.querySelector('.message-timestamp, .timestamp, mws-message-status time, [data-e2e-message-timestamp]');
    if (timeEl) {
      msgTime = timeEl.innerText.trim();
    }

    var textParts = wrapper.querySelectorAll('mws-text-message-part');
    textParts.forEach(function(part) {
      var text = part.innerText.trim();
      if (text) {
        messages.push({
          from: isOutgoing ? 'You' : partnerName,
          text: text,
          timestamp: msgTime || currentDateLabel || '',
          isOutgoing: isOutgoing
        });
      }
    });
  });

  // Return the last N messages
  var sliced = messages.slice(-limit);

  return {
    status: 'ok',
    partnerName: partnerName,
    totalMessages: messages.length,
    returned: sliced.length,
    messages: sliced
  };
}


// ─────────────────────────────────────────────
// INTERNAL HELPER: find the visible send button
// Google Messages renders TWO send buttons — one is a hidden
// 0×0 ghost that querySelector returns first. We need the one
// with actual screen dimensions.
// ─────────────────────────────────────────────
function _findVisibleSendButton() {
  var btns = document.querySelectorAll('button.send-button');
  for (var i = 0; i < btns.length; i++) {
    var rect = btns[i].getBoundingClientRect();
    if (rect.width > 0 && rect.height > 0) return btns[i];
  }
  return null;
}


// ─────────────────────────────────────────────
// INTERNAL HELPER: poll for a condition with timeout
// Returns the truthy result of checkFn, or null on timeout.
// ─────────────────────────────────────────────
async function _poll(checkFn, intervalMs, timeoutMs) {
  var elapsed = 0;
  while (elapsed < timeoutMs) {
    var result = checkFn();
    if (result) return result;
    await new Promise(function(r) { setTimeout(r, intervalMs); });
    elapsed += intervalMs;
  }
  return null;
}


// ─────────────────────────────────────────────
// INTERNAL HELPER: type text into the compose box and locate the send button
// Shared by sendMessage and startNewMessage.
//
// IMPORTANT: Google Messages uses Angular Material buttons that reject
// programmatic JS clicks (untrusted events). After this function types
// the message, the caller MUST use the Chrome computer tool to physically
// click the send button at the returned coordinates.
//
// Returns: { status: 'ready_to_send', sendButtonCoords: {x, y} }
//      or: { status: 'error', error: '...' }
// ─────────────────────────────────────────────
async function _typeAndSend(text, recipientLabel) {
  // Poll for textarea (up to 3s)
  var textarea = await _poll(function() {
    return document.querySelector('mws-message-compose textarea.input');
  }, 100, 3000);

  if (!textarea) {
    console.log('❌ Could not find the message input box.');
    return { status: 'error', error: 'Message input box not found' };
  }

  textarea.focus();
  textarea.select();
  document.execCommand('selectAll', false, null);
  document.execCommand('insertText', false, text);
  textarea.dispatchEvent(new Event('input', { bubbles: true }));

  // Poll for the visible send button to be enabled (up to 2s)
  var sendBtn = await _poll(function() {
    var btn = _findVisibleSendButton();
    return (btn && !btn.disabled) ? btn : null;
  }, 100, 2000);

  if (!sendBtn) {
    sendBtn = _findVisibleSendButton();
    if (!sendBtn) {
      console.log('❌ Send button not found.');
      return { status: 'error', error: 'Send button not found' };
    }
  }

  // Return button coordinates for a trusted click via the computer tool
  var rect = sendBtn.getBoundingClientRect();
  var coords = {
    x: Math.round(rect.left + rect.width / 2),
    y: Math.round(rect.top + rect.height / 2)
  };

  console.log('📝 Message typed for ' + recipientLabel + '. Send button at (' + coords.x + ', ' + coords.y + ')');
  return { status: 'ready_to_send', sendButtonCoords: coords, recipient: recipientLabel };
}


// ─────────────────────────────────────────────
// 3. SEND A MESSAGE TO AN EXISTING CONVERSATION
// Now async — returns a Promise that resolves after
// the message is actually sent (or errors).
// ─────────────────────────────────────────────
async function sendMessage(name, text) {
  var matches = _findMatches(name);

  if (matches.length === 0) {
    return { status: 'error', error: 'No conversation found for: "' + name + '"' };
  }

  if (matches.length > 1) {
    return {
      status: 'ambiguous',
      error: 'Multiple conversations match "' + name + '"',
      matches: matches.map(function(m) { return m.name; })
    };
  }

  var found = matches[0];
  var link = found.item.querySelector('a');
  if (link) link.click();

  var result = await _typeAndSend(text, found.name);
  result.name = found.name;
  // CALLER MUST: use computer tool to left_click at result.sendButtonCoords
  return result;
}


// ─────────────────────────────────────────────
// 4. START A NEW CONVERSATION
// Now async — returns a Promise that resolves after
// the message is actually sent (or errors).
// ─────────────────────────────────────────────
async function startNewMessage(phoneOrName, text) {
  var startBtn = Array.from(document.querySelectorAll('button, a')).find(function(el) {
    var label = (el.getAttribute('aria-label') || '').toLowerCase();
    var txt = (el.innerText || '').toLowerCase().trim();
    return txt === 'start chat' || label.includes('start chat');
  });

  if (!startBtn) {
    return { status: 'error', error: 'Could not find the "Start chat" button.' };
  }
  startBtn.click();

  // Poll for recipient input (up to 3s)
  var toInput = await _poll(function() {
    return document.querySelector(
      'mws-chips-input input, input[placeholder*="name"], input[placeholder*="phone"], input[placeholder*="To"]'
    );
  }, 100, 3000);

  if (!toInput) {
    console.log('❌ Could not find the recipient input field.');
    return { status: 'error', error: 'Recipient input not found' };
  }

  toInput.focus();
  var setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
  setter.call(toInput, phoneOrName);
  toInput.dispatchEvent(new Event('input', { bubbles: true }));
  toInput.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true }));

  // Wait for compose area to load after recipient selection
  await new Promise(function(r) { setTimeout(r, 1200); });

  var result = await _typeAndSend(text, phoneOrName);
  result.recipient = phoneOrName;
  // CALLER MUST: use computer tool to left_click at result.sendButtonCoords
  return result;
}


// ─────────────────────────────────────────────
// 5. BULK FETCH THREADS
// Async function — returns a Promise.
// Iterates through conversations visible in the sidebar,
// clicks into each one, extracts the full message thread,
// then moves to the next. All data is in memory from
// the initial PullMessages gRPC load — no network calls.
//
// Options:
//   maxConversations: number  — max threads to fetch (default: 25)
//   maxMessagesPerThread: number — per-thread message cap (default: 50)
//   daysBack: number — only fetch threads with activity in last N days (default: null = all)
//   namesOnly: string[] — if set, only fetch these names (default: null = all)
//   renderWaitMs: number — ms to wait for DOM render per conversation (default: 3000)
//
// Returns: { status, threadsFetched, totalMessages, elapsed, threads: [...] }
// Each thread: { name, convId, sidebarTime, messageCount, messages: [{from, text, timestamp, isOutgoing}] }
// ─────────────────────────────────────────────
async function bulkFetchThreads(options) {
  options = options || {};
  var maxConversations = options.maxConversations || 25;
  var maxMsgsPerThread = options.maxMessagesPerThread || 50;
  var daysBack = options.daysBack || null;
  var namesOnly = options.namesOnly || null;
  var renderWaitMs = options.renderWaitMs || 3000;

  var t0 = performance.now();

  // ── Step 1: Scroll the sidebar to load all conversations ──
  var nav = document.querySelector('mws-conversations-list nav') || document.querySelector('mws-conversations-list');
  if (nav) {
    var prevCount = 0;
    var stableRounds = 0;
    while (stableRounds < 3) {
      nav.scrollTop = nav.scrollHeight;
      await new Promise(function(r) { setTimeout(r, 600); });
      var currentCount = document.querySelectorAll('mws-conversation-list-item').length;
      if (currentCount === prevCount) {
        stableRounds++;
      } else {
        prevCount = currentCount;
        stableRounds = 0;
      }
      // Safety: don't scroll forever
      if (currentCount >= maxConversations * 2) break;
    }
    // Scroll back to top so we can click items
    nav.scrollTop = 0;
    await new Promise(function(r) { setTimeout(r, 300); });
  }

  // ── Step 2: Collect conversation metadata from sidebar ──
  var items = document.querySelectorAll('mws-conversation-list-item');
  var convMeta = [];

  Array.from(items).forEach(function(item) {
    var nameEl = item.querySelector('.name');
    var name = nameEl ? nameEl.textContent.trim() : '';
    var link = item.querySelector('a[href]');
    var href = link ? link.getAttribute('href') : '';
    var convId = href ? href.split('/conversations/')[1] : '';
    var timeEl = item.querySelector('mws-relative-timestamp');
    var time = timeEl ? timeEl.textContent.trim() : '';
    var snippetEl = item.querySelector('mws-conversation-snippet');
    var snippet = snippetEl ? snippetEl.textContent.trim() : '';

    convMeta.push({ name: name, convId: convId, time: time, snippet: snippet, link: link, element: item });
  });

  // ── Step 3: Apply filters ──
  var filtered = convMeta;

  // Filter by daysBack
  if (daysBack) {
    var cutoff = new Date();
    cutoff.setDate(cutoff.getDate() - daysBack);
    filtered = filtered.filter(function(c) {
      // Parse relative times like "5 min", "2 hr", "Yesterday", "Feb 16", "Jan 3"
      var t = c.time.toLowerCase();
      if (t.includes('min') || t.includes('hr') || t.includes('hour') || t === 'now') return true;
      // Time-of-day like "2:01 PM" or "9:48 AM" means today
      if (t.match(/^\d{1,2}:\d{2}\s*(am|pm)$/)) return true;
      if (t.includes('yesterday')) return daysBack >= 1;
      // Try parsing as a date
      var parsed = new Date(t + (t.match(/\d{4}/) ? '' : ', ' + new Date().getFullYear()));
      if (!isNaN(parsed.getTime())) {
        return parsed >= cutoff;
      }
      // If we can't parse it, include it (conservative)
      return true;
    });
  }

  // Filter by namesOnly
  if (namesOnly && namesOnly.length > 0) {
    var lowerNames = namesOnly.map(function(n) { return n.toLowerCase(); });
    filtered = filtered.filter(function(c) {
      var cn = c.name.toLowerCase();
      return lowerNames.some(function(n) { return cn.includes(n); });
    });
  }

  // Cap at maxConversations
  filtered = filtered.slice(0, maxConversations);

  // ── Step 4: Iterate and extract threads ──
  var threads = [];
  var totalMessages = 0;

  for (var i = 0; i < filtered.length; i++) {
    var conv = filtered[i];

    // Navigate to conversation — prefer fresh sidebar link, fall back to direct URL
    var navigated = false;
    if (conv.convId) {
      // Find the link in current DOM by href (handles Angular re-ordering)
      var freshLink = document.querySelector('a[href*="/conversations/' + conv.convId + '"]');
      if (freshLink) {
        freshLink.click();
        navigated = true;
      }
    }
    if (!navigated && conv.link && conv.link.isConnected) {
      conv.link.click();
      navigated = true;
    }
    if (!navigated) continue;

    // Phase 1: Wait for old messages to clear (max 500ms)
    for (var c = 0; c < 10; c++) {
      await new Promise(function(r) { setTimeout(r, 50); });
      if (document.querySelectorAll('mws-message-wrapper').length === 0) break;
    }

    // Phase 2: Wait for new messages to appear
    var rendered = false;
    for (var w = 0; w < Math.ceil(renderWaitMs / 50); w++) {
      await new Promise(function(r) { setTimeout(r, 50); });
      if (document.querySelectorAll('mws-message-wrapper').length > 0) {
        rendered = true;
        break;
      }
    }

    // Extra settle time if we got messages
    if (rendered) {
      await new Promise(function(r) { setTimeout(r, 150); });
    }

    // Get partner name — use sidebar name, clean up prefixes like "Muted"
    var partnerName = conv.name.replace(/^Muted\s+/i, '').trim() || conv.name;

    // Extract messages
    var messages = [];
    var currentDateLabel = '';
    var wrappers = document.querySelectorAll('mws-message-wrapper');

    Array.from(wrappers).forEach(function(wrapper) {
      // Check for date separator
      var prev = wrapper.previousElementSibling;
      while (prev) {
        if (prev.classList && (prev.classList.contains('date-separator') ||
            prev.tagName === 'MWS-RELATIVE-TIMESTAMP' ||
            prev.classList.contains('separator'))) {
          currentDateLabel = prev.innerText.trim();
          break;
        }
        if (prev.tagName === 'MWS-MESSAGE-WRAPPER') break;
        prev = prev.previousElementSibling;
      }

      var isOutgoing = wrapper.getAttribute('is-outgoing') === 'true';
      var msgTime = '';
      var timeEl = wrapper.querySelector('.message-timestamp, .timestamp, mws-message-status time, [data-e2e-message-timestamp]');
      if (timeEl) msgTime = timeEl.innerText.trim();

      var textParts = wrapper.querySelectorAll('mws-text-message-part');
      textParts.forEach(function(part) {
        var text = part.innerText.trim();
        if (text) {
          messages.push({
            from: isOutgoing ? 'You' : partnerName,
            text: text,
            timestamp: msgTime || currentDateLabel || '',
            isOutgoing: isOutgoing
          });
        }
      });
    });

    // Cap messages per thread
    var sliced = messages.slice(-maxMsgsPerThread);
    totalMessages += sliced.length;

    threads.push({
      name: partnerName || conv.name,
      convId: conv.convId,
      sidebarTime: conv.time,
      messageCount: sliced.length,
      messages: sliced
    });
  }

  var elapsed = Math.round(performance.now() - t0);

  return {
    status: 'ok',
    threadsFetched: threads.length,
    totalMessages: totalMessages,
    elapsedMs: elapsed,
    threads: threads
  };
}
