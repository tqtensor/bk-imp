// Some math operators
#let prox = [#math.op("prox")]
#let proj = [#math.op("proj")]
#let argmin = [#math.arg]+[#math.min]

// Initiate the document title, author...
#let assignment_class(title, author, course_id, professor_name, semester, body) = {
  set document(title: title, author: author)
  set page(
    paper:"a4",
    header: locate(
        loc => if (
            counter(page).at(loc).first()==1) { none }
        else if (counter(page).at(loc).first()==2) { align(right,
              [*#author* | *#course_id: #title*]
            ) }
        else {
            align(right,
              [*#author* | *#course_id: #title*]
            )
        }
    ),
    footer: locate(loc => {
      let page_number = counter(page).at(loc).first()
      let total_pages = counter(page).final(loc).last()
      align(center)[Page #page_number of #total_pages]
    }))
  block(height:25%,fill:none)
  align(center, text(17pt)[
    *#course_id: #title*])
  align(center, [_Prof. #professor_name _, #semester])
  block(height:35%,fill:none)
  align(center)[*#author*]

  pagebreak(weak: false)
  body
}
