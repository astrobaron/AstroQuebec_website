---
title: Activities

type: landing

cascade:
  profile: false

sections:
  - block: google-calendar
    content:
      embed_url: "https://calendar.google.com/calendar/embed?src=8c93e58e81334542ce90c2bd39b7b800b716aa5aa01419c321a525c43078933a%40group.calendar.google.com&ctz=America%2FToronto&hl=en&wkst=2&mode=MONTH&showPrint=0"

  - block: markdown
    content:
      title: Annual meeting
      subtitle: ''
      text: |
        The annual meeting of AstroQuébec brings together the community to review scientific progress, research initiatives, training activities, and the centre’s collaborations.

        It is also an opportunity to present new projects, discuss the challenges of astrophysics research, and strengthen ties between researchers, students, and partners across Quebec.

        {{% cta cta_link="/activites/rencontre-annuelle/" cta_text="More information" %}}

    design:
      columns: '1'

  - block: events-nearest
    content:
      title: Recent events
      count: 50
      page_type: event
      filters:
        exclude_featured: false
      order: desc
    design:
      view: compact
      columns: '1'
---
