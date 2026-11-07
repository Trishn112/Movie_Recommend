"""Calendar rendering helpers for upcoming TMDB releases."""
import calendar
from collections import defaultdict
from datetime import date
import streamlit as st

def render_upcoming_calendar(movies):
    today = date.today()
    dated = defaultdict(list)
    for movie in movies:
        raw = movie.get("release_date") or ""
        try:
            release = date.fromisoformat(raw[:10])
        except (ValueError, TypeError):
            continue
        if release >= today:
            dated[release].append(movie)
    if not dated:
        st.info("No dated upcoming releases were returned for this period.")
        return
    first_month = min(dated)
    last_month = max(dated)
    month_options=[]
    year, month = first_month.year, first_month.month
    while (year, month) <= (last_month.year, last_month.month):
        month_options.append(date(year, month, 1))
        month += 1
        if month == 13: year, month = year+1, 1
    chosen = st.selectbox("Choose release month", month_options, format_func=lambda d: d.strftime("%B %Y"), key="upcoming_calendar_month")
    st.markdown(f"### {chosen.strftime('%B %Y')} — release calendar")
    cal=calendar.Calendar(firstweekday=calendar.MONDAY)
    weekdays=["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    cols=st.columns(7)
    for col, label in zip(cols, weekdays): col.markdown(f"**{label}**")
    for week in cal.monthdayscalendar(chosen.year, chosen.month):
        cols=st.columns(7)
        for col, day in zip(cols, week):
            with col:
                if day == 0:
                    st.markdown(" ")
                    continue
                release_day=date(chosen.year, chosen.month, day)
                day_movies=dated.get(release_day, [])
                if day_movies:
                    st.markdown(f"**:blue[{day}]** · {len(day_movies)}")
                    for movie in day_movies[:3]:
                        st.caption(movie.get("title", "Untitled"))
                    if len(day_movies)>3: st.caption(f"+{len(day_movies)-3} more")
                else:
                    st.caption(str(day))
    st.divider()
    st.markdown("### Releases this month")
    month_movies=sorted([(d, items) for d,items in dated.items() if d.year==chosen.year and d.month==chosen.month], key=lambda x:x[0])
    if not month_movies:
        st.info("No upcoming movies scheduled for this month.")
    for release_day, items in month_movies:
        st.markdown(f"**{release_day.strftime('%A, %d %B %Y')}**")
        from cards import show_live_movies
        show_live_movies(items, f"upcoming_{release_day.isoformat()}")
