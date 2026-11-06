---
layout: post
title: "Building an Automated Customer Feedback Loop with Open Source Tools"
date: 2027-01-05
author: "ARDOT Consulting"
tags: [customer-feedback, automation, open-source, formbricks, chatwoot, n8n, ollama, metabase]
excerpt: "Collect, analyze, and act on customer feedback automatically — without sending your data to a third-party survey platform."
---

You already know customer feedback matters. The problem isn't knowing that — it's the gap between collecting feedback and actually doing something with it. Most small businesses fall into one of two traps: they collect feedback sporadically (a survey sent once a year that gets a 12% response rate), or they collect it constantly but never analyze it (a support inbox full of unread complaints and compliments).

Neither version helps you improve. What helps is a loop: collect → analyze → act → follow up → repeat. And while that sounds like a lot of manual work, it doesn't have to be. Open source tools can handle every stage of this loop, on infrastructure you control, without per-response pricing or vendor lock-in.

Here's how to build it.

## Why Most Feedback Systems Fail

Before we get to the tools, let's name the real problem. Most feedback systems aren't systems at all — they're one-off efforts. A business sends a survey after a project wraps. Someone reads the results, mentions a few highlights at the next team meeting, and then the spreadsheet sits in a shared drive until next year.

This fails for three reasons:

1. **Timing.** Feedback collected weeks after an interaction is less specific and less honest. Customers forget the details. You get vague sentiment instead of actionable insight.

2. **Volume.** When feedback trickles in through emails, support tickets, review sites, and the occasional survey, no one person has the full picture. Patterns get missed.

3. **No closing the loop.** Customers who take the time to give feedback and hear nothing back don't give feedback again. The response rate on your next survey drops.

An automated feedback loop addresses all three. It collects feedback at the right moment, consolidates it into one place, uses AI to surface patterns, and automatically acknowledges every customer who responds.

## The Open Source Stack

| Tool | Role | License |
|---|---|---|
| **Formbricks** | Survey and feedback collection (NPS, CSAT, in-app, link surveys) | AGPL-3.0 |
| **Chatwoot** | Conversational feedback via live chat, email, and social DMs | MIT (community edition) |
| **n8n** | Workflow orchestration — connects everything | Sustainable Use License |
| **Ollama** | Local LLM for sentiment analysis and theme extraction | MIT |
| **Metabase** | Dashboards — visualize feedback trends over time | AGPL-3.0 |

All five are self-hostable. Your customer feedback data — which often includes names, order details, and candid opinions — stays on your server, not in a vendor's cloud.

If you've followed our earlier guides, you may already have some of these running. n8n and Ollama power many of the workflows we've covered. Metabase is the same tool we use for [business analytics](/blog/2026/09/30/self-hosting-metabase-open-source-business-analytics-without-saas/). The two new pieces are Formbricks for structured surveys and Chatwoot for conversational feedback.

## Stage 1: Collect Feedback at the Right Moment

The first piece is timing. You want feedback collected automatically at specific trigger points — after a purchase, after a support ticket closes, after a project milestone — not batched into an annual survey.

### Structured Surveys with Formbricks

[Formbricks](https://formbricks.com/) is an open source experience management platform. Think of it as a self-hosted Qualtrics. It handles NPS scores, CSAT ratings, open-text feedback, and multi-step surveys, and it can deliver them as link surveys (emailed or texted), website widgets, or in-app popups.

The key feature for automation is the **API**. You don't have to manually send survey links — n8n can trigger a Formbricks survey at the right moment:

- **After a purchase:** n8n listens for a new order in your e-commerce system (Odoo, Invoice Ninja, or whatever you use), waits 48 hours, and emails a link to a post-purchase survey.
- **After a support ticket closes:** n8n detects the resolution in Chatwoot (or your help desk), waits 24 hours, and sends a CSAT survey.
- **After project milestones:** For service businesses, n8n can send a pulse survey after each project phase rather than waiting until the engagement ends.

Each survey should be short. One rating question (NPS: "How likely are you to recommend us?" or CSAT: "How satisfied were you with your recent experience?") plus one open-text field ("What's one thing we could do better?"). Response rates on three-question surveys are dramatically higher than on fifteen-question surveys.

### Conversational Feedback with Chatwoot

Not all feedback comes through surveys. A lot of it arrives as offhand comments in support chats, emails, or social media messages — "Your checkout was confusing" or "The new dashboard is so much faster." This is valuable feedback, but it usually gets buried in support conversations.

[Chatwoot](https://www.chatwoot.com/) is an open source omnichannel customer support platform. It pulls conversations from live chat, email, WhatsApp, and social media into a shared inbox. Every conversation is already tagged by channel and can be labeled by topic. The feedback is there — it just needs to be routed into your analysis pipeline.

The trick is to use Chatwoot's conversation labels strategically. Train your team to label feedback-bearing messages with a "feedback" tag (or set up a simple n8n workflow that auto-tags messages containing keywords like "suggestion," "confusing," "love," "hate," "wish"). Once tagged, those messages flow into the same analysis pipeline as your survey responses.

## Stage 2: Analyze Feedback Automatically

This is where most manual feedback processes break down. Reading 200 survey responses and 50 support messages by hand, then summarizing them for the team, takes hours. And the summary is usually subjective — one person's reading of what matters most.

A local LLM changes this. Instead of sending your customer feedback to an external AI API, you run [Ollama](/blog/2026/08/20/running-local-llms-with-ollama-a-practical-guide-for-businesses/) on your own server. The feedback data never leaves your infrastructure.

### What the LLM Does

For each piece of incoming feedback — whether a survey response or a tagged support message — an n8n workflow sends it to Ollama with a structured prompt:

```
You are a customer feedback analyst. Analyze this feedback and return a JSON object with:
- sentiment: "positive", "negative", or "neutral"
- category: one of "product", "service", "pricing", "support", "onboarding", "other"
- priority: "high", "medium", or "low" (high = urgent issue affecting multiple customers)
- summary: a one-sentence summary of the core point
- action_suggested: a brief suggestion for what to do about it

Feedback: {{ feedback_text }}
```

The LLM returns structured data. n8n stores the original feedback, the sentiment, the category, the priority, and the summary in a database (Directus, NocoDB, or even a simple Postgres table). This gives you a searchable, filterable record of every piece of feedback your business receives — automatically categorized, automatically tagged for urgency.

### What the LLM Doesn't Do

It doesn't make decisions. The LLM surfaces patterns and drafts summaries, but a human decides what to act on. If the model flags something as high priority, someone on your team reviews it. If it categorizes a message as "pricing" feedback, someone confirms that's accurate before it goes into a pricing report.

The goal is to compress 200 responses into a dashboard you can scan in 5 minutes — not to replace the judgment of someone who knows your business.

### Weekly Theme Extraction

In addition to per-response analysis, run a weekly batch job that feeds all the week's feedback into the LLM and asks for a theme summary:

```
Here are all customer feedback responses from this week. Identify the top 3 themes 
(positive or negative) that appear across multiple responses. For each theme, provide:
- The theme name
- How many responses mentioned it
- A representative quote
- Whether this is a new theme or a recurring one

Responses:
{{ weekly_feedback }}
```

This weekly digest goes to your team automatically — posted in Mattermost, emailed to managers, or both. No one has to compile it. The themes are data-driven, not anecdotal.

## Stage 3: Act on What You Find

Analysis without action is just expensive filing. The feedback loop has to connect to your operations.

### Routing by Priority

The n8n workflow that analyzes feedback also routes it:

- **High priority** (urgent issues, multiple complaints about the same thing): Route immediately to a Mattermost or email alert for the relevant team lead. If three customers report a checkout bug in one day, you don't want to wait for the weekly digest.
- **Medium priority** (recurring issues, improvement suggestions): Add to a feedback backlog in your project management tool. We've covered [open source project management alternatives](/blog/2026/10/14/open-source-project-management-tools-that-replace-asana/) — use whichever one your team already works in.
- **Low priority** (minor suggestions, one-off comments): Log for trend analysis but don't route individually.

### Closing the Loop with Customers

This is the step most businesses skip. When a customer gives you feedback — especially negative feedback — and you fix the problem, tell them. This is the single highest-ROI action in the entire feedback loop.

n8n can automate this. When a feedback item is marked as "resolved" in your project management tool, the workflow:

1. Looks up the original feedback submission
2. Sends the customer a personalized follow-up: "You mentioned X was a problem. We've fixed it — here's what changed."

This doesn't require AI-generated text. A template with the customer's name, their original feedback summary, and the resolution note is enough. The message is short, honest, and specific. It tells the customer that their feedback went somewhere — which means they'll give you feedback again next time.

For positive feedback, a simpler automation: if a customer gives you a 9 or 10 NPS score, n8n sends a thank-you email with a link to leave a public review (on whatever platform matters to your industry). This is how you turn satisfied customers into advocates without manually emailing each one.

## Stage 4: Visualize Trends

Individual feedback items help you fix today's problems. Trend data helps you fix tomorrow's.

Connect your feedback database to [Metabase](/blog/2026/09/30/self-hosting-metabase-open-source-business-analytics-without-saas/) and build a simple dashboard:

- **NPS or CSAT trend over time** (line chart, updated weekly)
- **Feedback volume by category** (bar chart — are pricing complaints increasing?)
- **Sentiment ratio by month** (what percentage of feedback is positive vs. negative?)
- **Top 5 themes this quarter** (table, sorted by frequency)
- **Response rate by survey type** (are your post-purchase surveys getting more responses than your quarterly ones?)

Set up a monthly dashboard subscription in Metabase that emails the dashboard to your leadership team. This replaces the manual "state of customer satisfaction" report that someone used to spend an afternoon assembling.

## The Full Workflow

Here's what the complete automated feedback loop looks like end to end:

1. **Trigger:** Customer completes a purchase, a support ticket closes, or a project milestone is reached.
2. **Collect:** n8n triggers a Formbricks survey at the right interval (24–48 hours later).
3. **Capture:** Customer responds. Concurrently, Chatwoot conversations with "feedback" labels feed into the same pipeline.
4. **Analyze:** n8n sends each response to Ollama for sentiment, category, priority, and summary.
5. **Store:** Structured analysis is saved to your database.
6. **Route:** High-priority items trigger immediate alerts. Medium items go to the backlog. Low items are logged.
7. **Summarize:** Weekly, n8n runs a theme extraction batch and posts the digest to your team.
8. **Act:** Team addresses items in priority order. When resolved, the item is marked complete.
9. **Close the loop:** n8n sends a follow-up to the customer whose feedback led to the fix.
10. **Visualize:** Metabase dashboard updates automatically, with a monthly subscription to leadership.

## What This Replaces

If you're currently using a commercial survey tool (Typeform, Qualtrics, SurveyMonkey) plus a separate support platform (Zendesk, Intercom) plus manual analysis, you're paying for three subscriptions and still doing the analysis by hand. The open source stack replaces all three for the cost of a single VPS — and the analysis, which is the part that used to eat your team's time, runs automatically.

| What you're paying now | Open source replacement |
|---|---|
| Survey tool ($25–75/mo) | Formbricks (self-hosted, $0 per response) |
| Support platform ($50–200/mo) | Chatwoot (self-hosted, $0 per user) |
| Manual analysis time (4–8 hrs/week) | Ollama + n8n (runs automatically) |
| Dashboard tool ($100+/mo) | Metabase (self-hosted, $0) |

## Getting Started

You don't need to build the entire loop at once. Start with one stage:

1. **Week 1–2:** Self-host Formbricks and set up one post-purchase survey. Get the collection piece working before you add analysis.
2. **Week 3–4:** Add the n8n workflow that sends each response to Ollama for sentiment and category. Store the results in a simple database table.
3. **Week 5–6:** Connect Metabase and build the dashboard. Start reviewing the weekly theme digest with your team.
4. **Week 7–8:** Add the routing automation and customer follow-up workflows. Close the loop.

By the end of two months, you have a feedback system that runs on its own — collecting at the right moments, analyzing in seconds, routing to the right people, and following up with customers automatically. Your team's role shifts from compiling feedback to acting on it, which is what they should have been doing all along.

---

*Ready to build a customer feedback system that actually closes the loop? [Contact ARDOT Consulting](/#contact) — we help businesses design, deploy, and maintain open source automation stacks tailored to their workflows.*
