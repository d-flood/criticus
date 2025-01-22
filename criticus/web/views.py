import traceback
from pathlib import Path

from django.conf import settings as conf
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from saxonche import PySaxonProcessor

from criticus.py import ce_config, combine_xml
from criticus.py.export_to_docx.xml_to_docx import export_xml_to_docx
from criticus.py.md2tei import markdown_to_tei as md2tei
from criticus.py.reformat_collation import reformat_xml
from criticus.py.tei2json.tei_to_json import tei_to_json as tei2json
from criticus.py.txt2json import convert_text_to_json as txt2json
from criticus.web import models


async def get_settings():
    settings_object, _ = await models.Settings.objects.aget_or_create(name="default")
    return settings_object


async def update_settings(data: dict):
    settings = await get_settings()
    for key, value in data.items():
        setattr(settings, key, value)
    await settings.asave()
    return settings


def error_response(request: HttpRequest, modal_text: str, error_text: str = None):
    context = {
        "modal_title": "Error",
        "modal_text": modal_text,
        "error_text": error_text,
        "status": "fail",
    }
    resp = render(request, "_modal.html", context)
    resp["HX-Retarget"] = "#modals"
    return resp


def success_response(request: HttpRequest, modal_text: str):
    context = {
        "modal_title": "Success",
        "modal_text": modal_text,
        "status": "success",
    }
    resp = render(request, "_modal.html", context)
    resp["HX-Retarget"] = "#modals"
    return resp


def warning_response(request: HttpRequest, modal_text: str, error_text: str = None):
    context = {
        "modal_title": "Warning",
        "modal_text": modal_text,
        "error_text": error_text,
        "status": "warning",
    }
    resp = render(request, "_modal.html", context)
    resp["HX-Retarget"] = "#modals"
    return resp


async def home(request: HttpRequest):
    context = {
        "page": "home",
    }
    return render(request, "index.html", context)


async def plain_text_to_json(request: HttpRequest):
    if request.method == "POST":
        print(request.POST)
        if not request.POST.get("single-ref"):  # convert all or some in file
            try:
                txt2json.convert_text_to_json(
                    filename=request.POST.get("input_file"),
                    output_dir=request.POST.get("output_directory"),
                    convert_all=bool(
                        request.POST.get("all-or-range") == "all_verses_in_file"
                    ),
                    reference_prefix=request.POST.get("unit-prefix"),
                    auto=bool(request.POST.get("ref-prefix", "") == "auto"),
                    verse_from=request.POST.get("range-from"),
                    verse_to=request.POST.get("range-to"),
                    siglum=request.POST.get("siglum"),
                )
                context = {
                    "modal_title": "Success",
                    "modal_text": "Your text file has been converted to JSON files.",
                    "status": "success",
                }
            except Exception as e:
                context = {
                    "modal_title": "Error",
                    "modal_text": f"An error occurred: {e}",
                    "error_text": traceback.format_exc(),
                    "status": "fail",
                }
                print(traceback.format_exc())
        else:  # convert from directly provided text
            try:
                txt2json.convert_single_verse_to_json(
                    text=request.POST.get("input_text"),
                    siglum=request.POST.get("siglum"),
                    reference=request.POST.get("single-ref"),
                    output_dir=request.POST.get("output_directory"),
                )
                context = {
                    "modal_title": "Success",
                    "modal_text": "Your text has been converted to a JSON file.",
                    "status": "success",
                }
            except Exception as e:
                context = {
                    "modal_title": "Error",
                    "modal_text": f"An error occurred: {e}",
                    "error_text": traceback.format_exc(),
                    "status": "fail",
                }
                print(traceback.format_exc())
        return render(request, "_modal.html", context)
    else:  # GET
        context = {
            "page": "txt2json",
        }
        return render(request, "plain_text_to_json.html", context)


async def markdown_to_tei(request: HttpRequest):
    if request.method == "POST":
        print(request.POST)
        try:
            md2tei.convert_md_to_tei(
                md_file=request.POST.get("input_file"),
                xml_file=request.POST.get("output_file"),
                output_format=request.POST.get("format"),
            )
            context = {
                "modal_title": "Success",
                "modal_text": f"Your Markdown file has been converted to TEI XML and saved to {request.POST.get('output_file')}.",
                "status": "success",
            }
        except Exception as e:
            context = {
                "modal_title": "Error",
                "modal_text": f"An error occurred: {e}",
                "error_text": traceback.format_exc(),
                "status": "fail",
            }
            print(traceback.format_exc())
        return render(request, "_modal.html", context)
    # GET
    context = {
        "page": "md2tei",
    }
    return render(request, "markdown_to_tei.html", context)


async def tei_to_json(request: HttpRequest):
    settings = await get_settings()

    if request.method == "POST":
        print(request.POST)
        single_verse = (
            request.POST.get("reference")
            if request.POST.get("range") == "one"
            else None
        )
        output_dir = request.POST.get("output_folder")
        siglum = request.POST.get("siglum")
        siglum_suffix = request.POST.get("siglum-suffix")
        output_file = (
            f"{output_dir}/{siglum}-{siglum_suffix}"
            if siglum_suffix
            else f"{output_dir}/{siglum}"
        )
        result = tei2json(
            tei_file_path=request.POST.get("input_file"),
            output_dir=output_dir,
            single_verse=single_verse,
            siglum_suffix=siglum_suffix,
            siglum=siglum,
            regexes=[r async for r in settings.tei2json_regexes.filter(active=True)],
        )
        if result is not True:
            return error_response(request, result)
        return success_response(
            request,
            f"Your TEI file has been converted to JSON files and saved to {output_file}.",
        )

    # GET
    context = {
        "page": "tei2json",
        "active_regexes": [
            r async for r in settings.tei2json_regexes.filter(active=True)
        ],
        "inactive_regexes": [
            r async for r in settings.tei2json_regexes.filter(active=False)
        ],
    }
    return render(request, "tei_to_json.html", context)


async def add_tei2json_regex(request: HttpRequest):
    settings = await get_settings()
    if request.method != "POST":
        return error_response(
            request, "Invalid request method. How'd you manage that? 🤔 -David"
        )
    expression = request.POST.get("newExpression")
    replacement = request.POST.get("newReplacement")
    if not expression or not replacement:
        return error_response(
            request, "Please provide both an expression and a replacement."
        )

    try:
        await models.CustomRegex.objects.acreate(
            settings=settings, expression=expression, replacement=replacement
        )
    except Exception as e:
        print(traceback.format_exc())
        return error_response(
            request, f"An error occurred: {e}", traceback.format_exc()
        )
    context = {
        "active_regexes": [
            r async for r in settings.tei2json_regexes.filter(active=True)
        ],
        "inactive_regexes": [
            r async for r in settings.tei2json_regexes.filter(active=False)
        ],
    }
    return render(request, "_regexes.html", context)


async def edit_tei2json_regex(request: HttpRequest, regex_pk: int):
    settings = await get_settings()
    if request.method == "POST":  # toggle active
        try:
            regex = await models.CustomRegex.objects.aget(pk=regex_pk)
            regex.active = not regex.active
            await regex.asave()
        except Exception as e:
            return error_response(
                request, f"An error occurred: {e}", traceback.format_exc()
            )
    elif request.method == "DELETE":  # delete
        try:
            regex = await models.CustomRegex.objects.aget(pk=regex_pk)
            await regex.adelete()
        except Exception as e:
            return error_response(
                request, f"An error occurred: {e}", traceback.format_exc()
            )
    else:
        return error_response(
            request, "Invalid request method. How'd you manage that? 🤔 -David"
        )
    context = {
        "active_regexes": [
            r async for r in settings.tei2json_regexes.filter(active=True)
        ],
        "inactive_regexes": [
            r async for r in settings.tei2json_regexes.filter(active=False)
        ],
    }
    return render(request, "_regexes.html", context)


async def combine_collations(request: HttpRequest):
    settings = await get_settings()
    if request.method == "POST":
        settings.combine_collations_input_dir = request.POST.get("input-folder", "")
        settings.combine_collations_output_file = request.POST.get("output-file", "")
        settings.combine_collations_startswith = request.POST.get("startswith", "")
        settings.combine_collations_title_stmt = request.POST.get("collation-title", "")
        settings.combine_collations_publication_stmt = request.POST.get(
            "publication-statement", ""
        )

        await settings.asave()
        _, failed = combine_xml.combine_xml_files(
            input_dir=request.POST.get("input-folder"),
            starts_with=request.POST.get("startswith"),
            base_dir=conf.BASE_DIR.as_posix(),
            save_path=request.POST.get("output-file"),
            already_reformatted=request.POST.get("reformatted") == "true",
            title_stmt=request.POST.get("collation-title"),
            publication_stmt=request.POST.get("publication-statement"),
        )
        if failed:
            return warning_response(
                request,
                "The following files failed to combine:",
                "\n".join(failed),
            )
        return success_response(request, "All collations combined successfully.")
    context = {
        "page": "combine_collations",
        "settings": settings,
    }
    return render(request, "combine_collations.html", context)


async def reformat_collation(request: HttpRequest):
    settings = await get_settings()
    if request.method == "POST":
        print(request.POST)
        if request.POST.get("reformat-type") == "reformat":
            result = reformat_xml.convert(
                xml_input_file=request.POST.get("input-file"),
                save_path=request.POST.get("output-file"),
                title_stmt=request.POST.get("collation-title"),
                publication_stmt=request.POST.get("publication-statement"),
            )
        else:  # clean witnesses
            result = reformat_xml.clean_wits(
                xml_input_file=request.POST.get("input-file"),
                save_path=request.POST.get("output-file"),
            )
        if result["type"] == "fail":
            return error_response(request, result["modal_text"], result["error_text"])
        elif result["type"] == "warning":
            return warning_response(request, result["modal_text"])
        return success_response(request, result["modal_text"])
    # GET
    context = {
        "page": "reformat_collation",
        "settings": settings,
    }
    return render(request, "reformat_collation.html", context)


async def tei_viewer(request: HttpRequest):
    settings = await get_settings()
    if request.method == "POST":
        print(request.POST)
        tei_folder = Path(request.POST.get("input-folder"))
        if not tei_folder.is_dir():
            return warning_response(request, "Please provide a valid folder.")

        settings.tei_viewer_input_dir = tei_folder.as_posix()
        await settings.asave()

        xml_files = list(tei_folder.glob("*.xml"))
        if not xml_files:
            return warning_response(
                request, "No XML files found in the provided folder."
            )
        return render(request, "_file_list.html", {"files": xml_files})
    else:  # GET
        return render(
            request, "tei_viewer.html", {"page": "tei-viewer", "settings": settings}
        )


async def get_tei_transcription(request: HttpRequest):
    """Get the content of an XML file, add a stylesheet, and return it."""
    xml_file = request.POST.get("xml_file")
    print(f"{xml_file=}")

    with PySaxonProcessor(license=False) as proc:
        xslt30_processor = proc.new_xslt30_processor()
        executable = xslt30_processor.compile_stylesheet(
            stylesheet_file=(
                conf.BASE_DIR / "resources" / "tei_transcription.xsl"
            ).as_posix()
        )
        output = executable.transform_to_string(source_file=xml_file)
        return HttpResponse(output, content_type="text/html")


async def configure_collation_editor(request: HttpRequest):
    settings = await get_settings()
    context = {
        "page": "ce-config",
        "settings": settings,
    }
    return render(request, "collation_editor.html", context)


async def load_collation_config(request: HttpRequest):
    print(request.GET)
    settings = await get_settings()
    try:
        config = ce_config.get_config(request.GET.get("input-file", ""))
    except Exception as e:
        return error_response(
            request, f"Failed to load the config file: {e}", traceback.format_exc()
        )
    settings.collation_editor_config_file = request.GET.get("input-file", "")
    await settings.asave()
    return render(request, "_collation_editor_options.html", {"config": config})


async def move_witnesses(request: HttpRequest):
    data = request.POST
    print(data)
    try:
        config = ce_config.get_config(data.get("input-file", ""))
    except Exception as e:
        return error_response(
            request, f"Failed to load the config file: {e}", traceback.format_exc()
        )
    move_type = data.get("moveType")
    if move_type in ("exclude", "include"):
        wits = (
            data.getlist("included-wits")
            if move_type == "exclude"
            else data.getlist("excluded-wits")
        )
        config = ce_config.move_selected_witnesses(config, wits, move_type)
    else:  # move_type == "delete"
        # delete from data["excluded_witnesses"]
        config = ce_config.delete_selected_witnesses(
            config, data.getlist("excluded-wits")
        )
    try:
        ce_config.save_config(config, data.get("input-file"))
    except Exception as e:
        return error_response(
            request, f"Failed to save the config file: {e}", traceback.format_exc()
        )
    try:
        config = ce_config.get_config(data.get("input-file"))
    except Exception as e:
        return error_response(
            request, f"Failed to reload the config file: {e}", traceback.format_exc()
        )
    return render(request, "_collation_editor_options.html", {"config": config})


async def update_collation_config(request: HttpRequest):
    data = request.POST
    try:
        config = ce_config.get_config(data.get("input-file"))
    except Exception as e:
        return error_response(
            request, f"Failed to load the config file: {e}", traceback.format_exc()
        )
    config["name"] = data.get("title")
    config["base_text"] = data.get("basetext")
    new_witness = data.get("new-witness")
    if new_witness:
        config["witnesses"].append(new_witness)
    try:
        ce_config.save_config(config, data.get("input-file"))
    except Exception as e:
        return error_response(
            request, f"Failed to save the config file: {e}", traceback.format_exc()
        )
    resp = render(request, "_collation_editor_options.html", {"config": config})
    resp["HX-Trigger"] = "updatedHeader"
    return resp


async def start_collation_editor(request: HttpRequest):
    config_path = request.GET.get("input-file")
    try:
        ce_config.start_ce(config_path)
    except Exception as e:
        return error_response(
            request,
            f"Failed to start the collation editor: {e}",
            traceback.format_exc(),
        )
    return success_response(
        request,
        "The collation editor has been started. There should be one (MacOS) or two (Windows) new terminal window(s) open, one for the CollateX server and one for the collation editor.",
    )


async def export_collation_to_docx(request: HttpRequest):
    settings = await get_settings()
    context = {
        "page": "export-collation",
        "settings": settings,
    }

    if request.method == "GET":
        return render(request, "export_collation.html", context)
    # POST
    print(request.POST)
    data = request.POST
    basetext_words_per_line = (
        int(data.get("basetext-words-per-line", 10))
        if data.get("basetext-words-per-line")
        else 10
    )
    result, msg = export_xml_to_docx(
        xml_filename=data.get("input-file"),
        output_filename=data.get("output-file"),
        basetext_words_per_line=basetext_words_per_line,
        text_wits_separator=data.get("text-wit-separator", " // "),
        rdg_n_text_separator=data.get("id-text-separator", ""),
        text_bold=data.get("rdg-bold", "true") == "true",
        wits_separator=data.get("wits-separator", ""),
        custom_template=data.get("custom-template", ""),
        use_custom_template=data.get("use-custom-template", "false") == "true",
        collapse_regularized=data.get("collapse-regularized", "false") == "true",
        add_suffix=data.get("add-suffix", "false") == "true",
    )
    if not result:
        return error_response(request, "An error occurred.", msg)
    settings.export_collation_input_file = data.get("input-file")
    settings.export_collation_output_file = data.get("output-file")
    settings.export_collation_add_suffix_to_child = (
        data.get("add-suffix", "false") == "true"
    )
    settings.export_collation_basetext_words_per_line = basetext_words_per_line
    settings.export_collation_collapse_regularized = (
        data.get("collapse-regularized", "false") == "true"
    )
    settings.export_collation_custom_template = data.get("custom-template", "")
    settings.export_collation_id_text_separator = data.get("id-text-separator", "")
    settings.export_collation_rdg_bold = data.get("rdg-bold", "") == "true"
    settings.export_collation_text_wits_separator = data.get(
        "text-wit-separator", " // "
    )
    settings.export_collation_use_custom_template = (
        data.get("use-custom-template", "false") == "true"
    )
    settings.export_collation_wits_separator = data.get("wits-separator", "")
    await settings.asave()
    return success_response(request, "The collation has been exported to a DOCX file.")
