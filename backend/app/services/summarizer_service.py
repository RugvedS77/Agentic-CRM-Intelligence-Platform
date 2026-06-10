def should_summarize(
    email_count: int
):
    return email_count >= 5

# Later:

# summary = llm.invoke(...)

# Store result in:

# threads.summary

# Then frontend can display:

# Executive Summary

# Alice initially inquired about
# nonprofit pricing.

# The organization purchased
# 10 seats and later requested
# an upgrade.

# Current request concerns
# prorated billing for 5
# additional seats.