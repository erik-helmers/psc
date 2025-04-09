# AUTO GENERATED FILE - DO NOT EDIT

#' @export
dangerouslySetInnerHtml <- function(id=NULL, value=NULL) {
    
    props <- list(id=id, value=value)
    if (length(props) > 0) {
        props <- props[!vapply(props, is.null, logical(1))]
    }
    component <- list(
        props = props,
        type = 'DangerouslySetInnerHtml',
        namespace = 'dangerously_set_inner_html',
        propNames = c('id', 'value'),
        package = 'dangerouslySetInnerHtml'
        )

    structure(component, class = c('dash_component', 'list'))
}
