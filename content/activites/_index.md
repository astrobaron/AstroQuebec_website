---
title: Activités

type: landing

cascade:
  profile: false

sections:
  - block: google-calendar
    content:
      embed_url: "https://calendar.google.com/calendar/embed?src=8c93e58e81334542ce90c2bd39b7b800b716aa5aa01419c321a525c43078933a%40group.calendar.google.com&ctz=America%2FToronto&hl=fr&wkst=2&mode=MONTH&showPrint=0"

  - block: markdown
    content:
      title: Rencontre annuelle
      subtitle: ''
      text: |
        La rencontre annuelle d’AstroQuébec rassemble la communauté pour faire le point sur les avancées scientifiques, les initiatives de recherche, la formation et les collaborations du centre.

        C’est aussi l’occasion de présenter les nouveaux projets, d’échanger autour des enjeux de la recherche en astrophysique et de renforcer les liens entre chercheuses, chercheurs, étudiants et partenaires du Québec.

        {{% cta cta_link="/activites/rencontre-annuelle/" cta_text="Plus d’informations" %}}
    design:
      columns: '1'

  - block: events-nearest
    content:
      title: Évènements récents
      count: 50
      page_type: event
      filters:
        exclude_featured: false
      order: desc
    design:
      view: compact
      columns: '1'
---
