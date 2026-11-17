---
# Leave the homepage title empty to use the site title
title:
date: 2022-10-24
type: landing

sections:
  - block: news-carousel
    content:
      title: Nouvelles
      subtitle:
      text:
      count: 5
      filters:
        author: ''
        category: ''
        exclude_featured: false
        publication_type: ''
        tag: ''
      offset: 0
      order: desc
      page_type: post
    design:
      view: card
      columns: '2'

  - block: activities-week
    content:
      title: Activités de la semaine
    design:
      columns: '1'

  - block: hero
    content:
      title: |
        AstroQuébec
      image:
        filename: 2024_rencontre_annuelle.jpeg
        credit: "Crédit photo : AstroQuébec"
      text: |
        <br>

        Le Centre de recherche en astrophysique du Québec (AstroQuébec) est un regroupement de chercheuses et chercheurs issus des Universités de Montréal, McGill, Laval et Bishop’s, dont la mission commune est de Comprendre l’Univers. Leurs travaux visent à répondre à des questions telles que d’où vient l’univers? De quoi est-il fait? Comment les galaxies et les étoiles y sont-elles apparues? Comment s’est formé le système solaire? Y a-t-il de la vie ailleurs que sur Terre? 
        
        AstroQuébec est financé par le Fonds de Recherche du Québec – Nature et Technologie. 
  - block: markdown
    id: mission
    content:
      title: Notre mission
      subtitle: ''
      text: |
        La mission d’AstroQuébec est de promouvoir l'excellence, la collaboration et le dynamisme en recherche en astrophysique au Québec, d’offrir un milieu d’accueil et de formation plus riche, plus diversifié et plus inclusif à la relève étudiante dans ce domaine, et de faire rayonner l’astronomie québécoise sur la scène mondiale.
    design:
      columns: '1'

  - block: markdown
    id: activites
    content:
      title: "[Activités](/activites/)"
      subtitle: ''
      text: |
        AstroQuébec organise des rencontres scientifiques, des ateliers de formation, des séminaires et des colloques, pour permettre à ses membres d’échanger entre eux et de se maintenir à jours sur les dernières avancées du domaine.
        
        AstroQuébec offre de plus plusieurs bourses de recherche à ses membres pour favoriser la formation de la relève, stimuler les collaborations scientifiques interinstitutionnelles et interdisciplinaires, et renforcer le rayonnement de la recherche en astrophysique au Québec et à l’international.

        AstroQuébec facilite aussi la mise en commun des ressources matérielles et humaines de ses membres pour une recherche scientifique de pointe et pour son rayonnement.
    design:
      columns: '1'

  - block: markdown
    content:
      title:
      subtitle:
      text: |
        {{% cta cta_link="./people/" cta_text="Consulter le répertoire" %}}
    design:
      columns: '1'
---
