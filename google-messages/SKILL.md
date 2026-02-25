---
name: google-messages
description: >
  Read and send Google Messages (Android SMS/RCS) via messages.google.com/web in Chrome.
  Use this skill whenever the user mentions checking texts, reading messages, sending a text,
  checking if someone messaged them, or anything involving their phone's SMS/RCS messages.
  Triggers include: "check my messages", "did anyone text me", "read my texts from X",
  "send a text to X", "reply to X", "what did X say", "any new messages", "start a conversation with X",
  "who have I been texting", "list my conversations".
  Requires Claude in Chrome with messages.google.com/web already open and signed in.
---

# Google Messages Skill

A Claude skill that gives you full read/write access to your Android phone's text messages (SMS and RCS) through the Google Messages web interface. No API keys, no authentication tokens — just a browser tab.

## What It Does

This skill lets Claude read, search, and send text messages on your behalf by automating the Google Messages web app (messages.google.com/web) via Claude in Chrome. It works with any Android phone that's paired to Google Messages for web.

**Reading messages**: Check for unread texts, read full conversation threads with any contact, or bulk-fetch multiple conversations at once for summarization and analysis.

**Sending messages**: Send replies to existing conversations or start new ones by phone number. Claude resolves partial names (e.g., "text John" → "John Condon") automatically.

**Bulk operations**: Fetch 5, 10, or 25+ conversation threads in a single call — useful for "summarize my recent texts" or "what have I been texting about this week?" workflows.

## Requirements

- **Claude in Chrome** extension installed and connected
- **Google Messages for web** (messages.google.com/web) open in a Chrome tab and paired with your Android phone
- That's it — no API keys, no OAuth, no server setup

## How It Works Under the Hood

Google Messages loads all your recent conversations into the browser's memory via gRPC when the page opens. This skill injects a JavaScript utility library into the page that reads and manipulates the DOM directly — no network calls, no API scraping. Each function call re-injects the full script (functions don't persist between Chrome tool calls), so it's stateless and resilient to page reloads.

The script handles Angular's DOM quirks: stale element references from component recycling, muted contact label parsing, conversation header name resolution, and a two-phase render-wait pattern for reliable navigation between threads.

## Functions at a Glance

| Function | What it does |
|---|---|
| `listConversations(limit)` | List all visible conversations with name, snippet, time, and unread status |
| `checkNewMessages()` | Return only unread conversations |
| `navigateToConversation("Name")` | Click into a specific conversation (partial name matching) |
| `extractMessages(limit)` | Read messages from the currently open conversation |
| `sendMessage("Name", "text")` | Send a message to an existing conversation (two-phase: returns coords, then click) |
| `startNewMessage("+1...", "text")` | Start a brand new conversation by phone number (two-phase) |
| `bulkFetchThreads(options)` | Fetch full threads from multiple conversations at once |

## Quick Examples

- **"Any new texts?"** → `checkNewMessages()`
- **"Read my messages with Amanda"** → `navigateToConversation("Amanda")` → wait → `extractMessages(40)`
- **"Text Ethan that I'll be there at 7"** → `sendMessage("Ethan Renaldi", "I'll be there at 7")` → click send button at returned coords
- **"Summarize my texts from the last 3 days"** → `bulkFetchThreads({ daysBack: 3, maxConversations: 10 })`

## Performance

Single conversation reads take about 3 seconds (navigate + render + extract). Bulk fetches run at roughly 1.5–2 seconds per thread, so 10 conversations takes about 16 seconds.

---

# Technical Reference

Everything below is the machine-facing instruction set that Claude reads when the skill triggers. You don't need to read this to use the skill — it's the implementation detail.

## Critical: Injection Rule

**JavaScript functions do NOT persist between separate `javascript_tool` calls.**
Always inject the full script AND call the target function in the **same single `javascript_tool` block**.
Never split injection and function call into separate tool calls — the second call will always fail
with "X is not defined".

Correct pattern (one block):
```javascript
// 1. Paste full script contents here...
function _findMatches(query) { ... }
function listConversations(limit) { ... }
// 2. Immediately call the function
listConversations(30);
```

## Prerequisites

- Claude in Chrome must be available and connected
- The user must have messages.google.com/web open in a browser tab and already signed in
- If the tab isn't open, ask the user to open it first

## Available Functions

| Function | Returns | Sync? |
|---|---|---|
| `listConversations(limit)` | `[{name, snippet, time, unread}]` | Yes — direct return |
| `checkNewMessages()` | `[{name, snippet, time}]` | Yes — direct return |
| `navigateToConversation("Name")` | `{status, name, matchCount}` | Yes — clicks and returns immediately |
| `extractMessages(limit)` | `{status, partnerName, messages: [{from, text, timestamp, isOutgoing}]}` | Yes — reads loaded DOM |
| `sendMessage("Name", "text")` | `{status: 'ready_to_send', name, sendButtonCoords: {x,y}}` | Async — requires physical click after |
| `startNewMessage("+1...", "text")` | `{status: 'ready_to_send', recipient, sendButtonCoords: {x,y}}` | Async — requires physical click after |
| `bulkFetchThreads(options)` | `{status, threadsFetched, totalMessages, elapsedMs, threads: [...]}` | Async — returns Promise |

**All data-reading functions return structured JSON directly as return values.** No console reading needed for list/check/extract operations.

### bulkFetchThreads — important notes

`bulkFetchThreads` is **async** and returns a Promise. You must invoke it with `.then()` or inside an async wrapper:
```javascript
// [full script here]
bulkFetchThreads({ maxConversations: 10, daysBack: 7, maxMessagesPerThread: 30 });
```
The `javascript_tool` handles Promise return values automatically — no special wrapping needed.

**Performance**: ~1.5–2 seconds per conversation. 5 threads ≈ 8 seconds, 10 threads ≈ 16 seconds.

**How it works**: All message data is loaded into Angular's memory on page load via gRPC PullMessages calls. bulkFetchThreads cycles through sidebar conversations by clicking each one, waiting for the DOM to render (~1.4s), then extracting messages — no additional network calls are made.

## Workflow

### Step 1: Find the messages.google.com tab

Use `tabs_context_mcp` to get available tabs, then identify the tab with `messages.google.com` in its URL.
If no such tab exists, tell the user: "Please open messages.google.com/web in Chrome and sign in, then ask me again."

### Step 2: Resolve the contact name (for send/read operations)

Users will often say "send a text to John" when the contact is stored as "John Condon".
Before sending or reading, resolve the name by injecting the full script and calling `listConversations(30)`
in one block. Parse the returned array to find the best match:

- Exactly one match → use that full name
- Zero matches → tell the user and show the full list
- Multiple matches → ask the user to clarify

You do NOT need to resolve names for `checkNewMessages()` or `startNewMessage()`.

### Step 3: Inject the full script + call the function (one block)

Read the script from `scripts/google_messages.js` (relative to this SKILL.md).
Paste its **entire contents** into the `javascript_tool` call, then append the function call at the end.

#### List all conversations
```javascript
// [full script here]
listConversations(30);
```

#### Check for new/unread messages
```javascript
// [full script here]
checkNewMessages();
```

#### Read a conversation (two-step process)

Reading uses two separate calls with a wait in between:

**Call 1 — Navigate:**
```javascript
// [full script here]
navigateToConversation("John Condon");
```
This clicks into the conversation and returns `{status: 'ok', name: 'John Condon'}` immediately.

**Wait 3 seconds** for the conversation to load in the DOM.

**Call 2 — Extract:**
```javascript
// [full script here]
extractMessages(40);
```
This reads the currently loaded conversation and returns structured data:
```json
{
  "status": "ok",
  "partnerName": "John Condon",
  "totalMessages": 85,
  "returned": 40,
  "messages": [
    {"from": "John Condon", "text": "Hey!", "timestamp": "Yesterday", "isOutgoing": false},
    {"from": "You", "text": "What's up?", "timestamp": "Yesterday", "isOutgoing": true}
  ]
}
```

If `extractMessages` returns `status: 'empty'`, wait 2 more seconds and call it again (re-injecting the full script).

The `limit` parameter defaults to 40 but can be increased for longer conversation history.

#### Send a message (two-phase: JS + physical click)

Google Messages uses Angular Material buttons that reject programmatic JS click events (untrusted events).
Sending requires two steps:

**Phase 1 — Inject script, navigate, and type the message:**
```javascript
// [full script here]
sendMessage("John Condon", "Your message here");
```
This returns `{ status: 'ready_to_send', name: 'John Condon', sendButtonCoords: { x: 1049, y: 522 } }`.
The message is typed into the compose box but NOT yet sent.

**Phase 2 — Click the send button with the Chrome `computer` tool:**
```
computer tool → action: left_click → coordinate: [x, y] from sendButtonCoords
```
Then take a screenshot to confirm the message appears in the conversation thread and the compose box is empty.

**IMPORTANT**: Always use the coordinates returned by `sendMessage` — never hardcode them. The button position varies with window size.

#### Start a new conversation (two-phase: JS + physical click)

Same two-phase pattern as sendMessage:

**Phase 1:**
```javascript
// [full script here]
startNewMessage("+13125550100", "Your message here");
```
Returns `{ status: 'ready_to_send', recipient: '+13125550100', sendButtonCoords: { x, y } }`.

**Phase 2:**
```
computer tool → action: left_click → coordinate: [x, y] from sendButtonCoords
```
Then screenshot to confirm.

#### Bulk fetch multiple conversation threads
```javascript
// [full script here]
bulkFetchThreads({
  maxConversations: 10,       // max threads to fetch (default: 25)
  maxMessagesPerThread: 30,   // per-thread message cap (default: 50)
  daysBack: 7,                // only threads active in last N days (default: null = all)
  namesOnly: ["Amanda", "Jonathan"],  // filter to specific names (default: null = all)
  renderWaitMs: 3000          // ms budget for DOM render per conversation (default: 3000)
});
```

Returns:
```json
{
  "status": "ok",
  "threadsFetched": 5,
  "totalMessages": 90,
  "elapsedMs": 8430,
  "threads": [
    {
      "name": "Amanda Lannert",
      "convId": "CgjinK_2GA5zHhIDNjU1",
      "sidebarTime": "3:12 PM",
      "messageCount": 20,
      "messages": [
        {"from": "Amanda Lannert", "text": "It's hard out there", "timestamp": "Feb 24", "isOutgoing": false},
        {"from": "You", "text": "Yah. Zoom for either.", "timestamp": "Feb 24", "isOutgoing": true}
      ]
    }
  ]
}
```

**When to use bulkFetchThreads vs single-conversation read:**
- User says "what have I been texting about lately?" → `bulkFetchThreads({ maxConversations: 10, daysBack: 3 })`
- User says "give me a summary of all my recent texts" → `bulkFetchThreads({ daysBack: 7 })`
- User says "read my messages with John" → single-conversation flow (navigateToConversation + extractMessages)

### Step 4: Read results and complete sends

**For listConversations / checkNewMessages / extractMessages / bulkFetchThreads:**
Read the return value from the tool call directly — it's structured JSON you can use immediately.
No `read_console_messages` needed.

**For sendMessage / startNewMessage — two-phase send:**
1. The JS call returns `{ status: 'ready_to_send', sendButtonCoords: { x, y } }` — the message is typed but NOT sent
2. Use the `computer` tool to `left_click` at the coordinates `[x, y]` from the response
3. Take a screenshot to confirm the message appears in the thread and the compose box is empty

If the JS call returns `status: 'error'`, handle the error (see Error handling below) and do NOT attempt a click.

### Step 5: Report results

- **listConversations**: show names clearly, note any unread
- **checkNewMessages**: list each unread conversation (name, time, preview)
- **extractMessages**: show messages in a clean readable format with timestamps, labeling each with sender's name
- **sendMessage / startNewMessage**: confirm success with a screenshot if needed
- **bulkFetchThreads**: summarize threads found (names, message counts), highlight key content

## Error handling

- `status: 'error'` with "No conversation found" → call `listConversations()` and show the user their full list
- `status: 'ambiguous'` → relay the matches array and ask user to clarify
- `status: 'empty'` from extractMessages → conversation didn't load yet; wait 2 seconds and retry
- `❌ Could not find the message input box` → conversation didn't load; wait and retry
- `status: 'ready_to_send'` → normal — proceed to phase 2 (physical click at sendButtonCoords)
- Send button coords returned but click didn't send → take screenshot, verify coords, try clicking again

## Example interactions

**User**: "Any new texts?"
→ Get tab → inject script + call `checkNewMessages()` in one block → present results

**User**: "Who have I been texting?"
→ Get tab → inject script + call `listConversations()` in one block → present list

**User**: "Read my messages with John"
→ Get tab → inject + `listConversations()` → resolve to "John Condon" → inject + `navigateToConversation("John Condon")` → wait 3s → inject + `extractMessages(40)` → present messages with timestamps

**User**: "Text John that I'm running 10 minutes late"
→ Get tab → inject + `listConversations()` → resolve to "John Condon" → inject + `sendMessage("John Condon", "Running about 10 minutes late, sorry!")` → returns `sendButtonCoords` → `computer` tool `left_click` at coords → screenshot to confirm

**User**: "Send a text to +1 312 555 0100 saying hey"
→ Get tab → inject + `startNewMessage("+13125550100", "hey")` → returns `sendButtonCoords` → `computer` tool `left_click` at coords → screenshot to confirm

**User**: "Give me a summary of my recent texts"
→ Get tab → inject + `bulkFetchThreads({ maxConversations: 10, daysBack: 3 })` → summarize threads

**User**: "What have Amanda and Jonathan been texting me about?"
→ Get tab → inject + `bulkFetchThreads({ namesOnly: ["Amanda", "Jonathan"], maxMessagesPerThread: 30 })` → present conversations
