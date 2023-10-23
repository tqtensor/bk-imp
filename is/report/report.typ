#import "template.typ": *
#let title = "Assignment: Customer Churn Prevention"
#let author = "Tang Quoc Thai - Ngo Trieu Long"
#let course_id = "Intelligent Systems"
#let instructor = "Quan Thanh Tho"
#let semester = "2nd Semester - 2023"
#set enum(numbering: "a)")
#set heading(numbering: "1.1)")
#set par(justify: true)
#set text(lang:"en", hyphenate:true)
#show: assignment_class.with(title, author, course_id, instructor, semester)

*Source code*: https://github.com/tqtensor

= Motivation

In recent years, there has been a growing trend within machine learning (ML) to integrate ML techniques into various aspects of business decision-making. This thesis report exemplifies an ML project focusing on developing an optimized incentive program for identifying and retaining customers at risk of switching to a competitor, commonly called "churning." This project extends a prevalent ML use case, namely customer churn prediction. It showcases the methodology employed to fine-tune an incentive program, aligning it with the core business objective of reducing customer churn. I have selected a prominent telecommunications company as our case study for this study.

= Key Features
- A churn predictor that predicts the probability of a customer becoming a churned user.
- An optimizer that optimizes the most optimal allocation of promotion to maximize profit but minimize promotion cost.
- An API endpoint.

= Design
== Overall Architecture

#figure(
  image("overall_architecture.jpg", width: 100%),
  caption: [Overall Architecture],
)

== UI Mockup

#figure(
  image("ui_mockup.png", width: 60%),
  caption: [UI Mockup],
)
