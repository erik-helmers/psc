
module DangerouslySetInnerHtml
using Dash

const resources_path = realpath(joinpath( @__DIR__, "..", "deps"))
const version = "0.0.1"

include("jl/dangerouslysetinnerhtml.jl")

function __init__()
    DashBase.register_package(
        DashBase.ResourcePkg(
            "dangerously_set_inner_html",
            resources_path,
            version = version,
            [
                DashBase.Resource(
    relative_package_path = "dangerously_set_inner_html.min.js",
    external_url = nothing,
    dynamic = nothing,
    async = nothing,
    type = :js
),
DashBase.Resource(
    relative_package_path = "dangerously_set_inner_html.min.js.map",
    external_url = nothing,
    dynamic = true,
    async = nothing,
    type = :js
)
            ]
        )

    )
end
end
