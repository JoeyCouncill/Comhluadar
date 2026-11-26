const countsUrl = document.currentScript.dataset.countsUrl;
const badges = document.querySelectorAll("[data-activity-badge]");
const chatForm = document.querySelector("[data-chat-seen-url]");
const csrfToken = chatForm?.querySelector("[name='csrfmiddlewaretoken']")?.value;

let needsChatAcknowledgement = Boolean(csrfToken);
let refreshing = false;

async function refreshActivityBadges() {
    if (document.hidden || refreshing) {
        return;
    }

    refreshing = true;

    try {
        if (needsChatAcknowledgement) {
            const seenResponse = await fetch(chatForm.dataset.chatSeenUrl, {
                method: "POST",
                mode: "same-origin",
                headers: { "X-CSRFToken": csrfToken },
                body: new URLSearchParams({seen_through: chatForm.dataset.seenThrough}),
            });

            needsChatAcknowledgement = seenResponse.status >= 500;
        }

        const response = await fetch(countsUrl, {headers: { Accept: "application/json" }});

        if (response.redirected || response.status === 401) {
            for (const badge of badges) {
                    badge.classList.add("d-none");
            }
            window.clearInterval(pollId);
            document.removeEventListener("visibilitychange", refreshActivityBadges);
            return;
        }

        if (!response.ok) {
            return;
        }

        const counts = await response.json();

        for (const badge of badges) {
        const count = counts[badge.dataset.activityBadge];
        badge.querySelector("[data-badge-value]").textContent = count;
        badge.classList.toggle("d-none", count === 0);
        }

    } catch {
        // Keep the last displayed counts and retry on the next refresh.
    } finally {
        refreshing = false;
    }
}

const pollId = window.setInterval(refreshActivityBadges, 60000);
document.addEventListener("visibilitychange", refreshActivityBadges);
refreshActivityBadges();