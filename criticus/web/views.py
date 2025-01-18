import traceback

from django.conf import settings as conf
from django.http import HttpRequest
from django.shortcuts import render

from criticus.py import combine_xml
from criticus.py.md2tei import markdown_to_tei as md2tei
from criticus.py.tei2json.tei_to_json import tei_to_json as tei2json
from criticus.py.txt2json import convert_text_to_json as txt2json
from criticus.web import models


async def get_settings():
    settings_object, _ = await models.Settings.objects.aget_or_create(name="default")
    return settings_object


def error_response(request: HttpRequest, modal_text: str, error_text: str = None):
    context = {
        "modal_title": "Error",
        "modal_text": modal_text,
        "error_text": error_text,
        "status": "fail",
    }
    resp = render(request, "_modal.html", context)
    resp["HX-Target"] = "#modals"
    return resp


def success_response(request: HttpRequest, modal_text: str):
    context = {
        "modal_title": "Success",
        "modal_text": modal_text,
        "status": "success",
    }
    resp = render(request, "_modal.html", context)
    resp["HX-Target"] = "#modals"
    return resp


def warning_response(request: HttpRequest, modal_text: str, error_text: str = None):
    context = {
        "modal_title": "Warning",
        "modal_text": modal_text,
        "error_text": error_text,
        "status": "warning",
    }
    resp = render(request, "_modal.html", context)
    resp["HX-Target"] = "#modals"
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
        print(request.POST)

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
