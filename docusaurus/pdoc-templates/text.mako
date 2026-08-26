<%!
  ## Custom pdoc3 markdown template for Docusaurus/MDX output.
  ##
  ## Emits semantic MDX component wrappers (ApiSignature, ApiMember) around
  ## generated API content so the Docusaurus theme controls presentation.
  ## Components are registered globally in docusaurus/src/theme/MDXComponents.
  import re

  # Docstring boilerplate injected by pydantic that adds noise to API docs.
  PYDANTIC_BOILERPLATE_SNIPPETS = (
      "Create a new model by parsing and validating input data",
      "The type of the None singleton.",
      "Usage docs: https://docs.pydantic.dev",
      "!!! abstract \"Usage Documentation\"",
  )

  # Members inherited from pydantic BaseModel machinery that add no value
  # to end-user API reference docs.
  PYDANTIC_NOISE_MEMBERS = {
      "model_config",
      "model_fields",
      "model_computed_fields",
      "model_post_init",
      "model_construct",
      "model_copy",
      "model_dump",
      "model_dump_json",
      "model_json_schema",
      "model_parametrized_name",
      "model_rebuild",
      "model_validate",
      "model_validate_json",
      "model_validate_strings",
  }

  SECTION_NAMES = (
      "Args", "Arguments", "Params", "Parameters", "Keyword Args",
      "Keyword Arguments", "Returns", "Return", "Yields", "Raises",
      "Warns", "Note", "Notes", "Example", "Examples", "Attributes",
      "See Also", "References", "Warnings",
  )

  _SECTION_RE = re.compile(
      r"^(?P<name>" + "|".join(SECTION_NAMES) + r"):\s*$"
  )

  # Sections whose body is a "name: description" item list. Other sections
  # (Example, Note, ...) keep their body verbatim (dedented) so code blocks
  # and prose survive intact.
  ITEMIZED_SECTIONS = {
      "Args", "Arguments", "Params", "Parameters", "Keyword Args",
      "Keyword Arguments", "Returns", "Return", "Yields", "Raises",
      "Warns", "Attributes",
  }
  _MKDOCS_XREF_RE = re.compile(r"\[([^\]]+)\]\[[^\]]*\]")


  def is_pydantic_boilerplate(text):
      text = (text or "").strip()
      if not text:
          return False
      return any(text.startswith(s) or s in text for s in PYDANTIC_BOILERPLATE_SNIPPETS)


  def clean_docstring(text):
      """Strip pydantic boilerplate paragraphs and unresolvable mkdocs-style
      cross references ([X][module.X] -> `X`)."""
      if not text:
          return ""
      paragraphs = re.split(r"\n\s*\n", text)
      kept = [p for p in paragraphs if not is_pydantic_boilerplate(p)]
      cleaned = "\n\n".join(kept).strip()
      cleaned = _MKDOCS_XREF_RE.sub(r"`\1`", cleaned)
      return cleaned


  def convert_google_sections(text):
      """Convert Google-style docstring sections (Args:, Returns:, ...) into
      markdown: a bold section label plus a bulleted list per item."""
      if not text:
          return ""
      lines = text.split("\n")
      out = []
      i = 0
      n = len(lines)
      in_code = False
      while i < n:
          line = lines[i]
          if line.strip().startswith("```"):
              in_code = not in_code
              out.append(line)
              i += 1
              continue
          m = None if in_code else _SECTION_RE.match(line.strip())
          if not m or (line and line[0] in " \t"):
              out.append(line)
              i += 1
              continue
          section = m.group("name")
          out.append("")
          out.append("**%s:**" % section)
          out.append("")
          i += 1
          # Collect the indented block belonging to this section.
          block = []
          while i < n:
              nxt = lines[i]
              if nxt.strip() and not nxt.startswith((" ", "\t")):
                  break
              block.append(nxt)
              i += 1
          out.extend(render_section_items(section, block))
          out.append("")
      return "\n".join(out)


  _ITEM_RE = re.compile(
      r"^(?P<indent>\s+)(?P<name>[\w\*\.\[\]\| ]+?)"
      r"(?:\s*\((?P<type>[^)]*)\))?:\s?(?P<desc>.*)$"
  )


  def dedent_block(block_lines):
      indents = [len(l) - len(l.lstrip()) for l in block_lines if l.strip()]
      cut = min(indents) if indents else 0
      return [l[cut:] if l.strip() else "" for l in block_lines]


  def render_section_items(section, block_lines):
      """Render an indented Google-section block as a markdown bullet list.
      Non-itemized sections (Example, Note, ...) are emitted verbatim."""
      if section not in ITEMIZED_SECTIONS or any(
          l.lstrip().startswith("```") for l in block_lines
      ):
          return dedent_block(block_lines)
      items = []
      current = None
      base_indent = None
      for raw in block_lines:
          if not raw.strip():
              if current is not None:
                  current[1].append("")
              continue
          indent = len(raw) - len(raw.lstrip())
          m = _ITEM_RE.match(raw)
          if m and (base_indent is None or indent <= base_indent):
              base_indent = indent if base_indent is None else base_indent
              name = m.group("name").strip()
              typ = (m.group("type") or "").strip()
              desc = m.group("desc").strip()
              label = "`%s`" % name if not name.startswith("*") else name
              if typ:
                  label += " (*%s*)" % typ
              current = (label, [desc] if desc else [])
              items.append(current)
          elif current is not None:
              current[1].append(raw.strip())
          else:
              # Non key: value content (e.g. Returns free text).
              items.append((None, [raw.strip()]))
      out = []
      for label, desc_lines in items:
          desc = " ".join(d for d in desc_lines if d).strip()
          if label:
              out.append("- **%s**: %s" % (label, desc) if desc else "- **%s**" % label)
          elif desc:
              out.append("%s" % desc)
      return out


  def format_signature(kind, name, params, returns):
      """Format a signature as a Python code block; multi-line when long."""
      prefix = {"class": "class ", "def": "def "}.get(kind, "")
      one_line = "%s%s(%s)%s" % (prefix, name, ", ".join(params), returns)
      if len(one_line) <= 78:
          return one_line
      lines = ["%s%s(" % (prefix, name)]
      for p in params:
          lines.append("    %s," % p)
      lines.append(")%s" % returns)
      return "\n".join(lines)


  def close_dangling_fences(text):
      """Terminate unclosed ``` fences so a docstring typo can't swallow the
      rest of the page (and break MDX parsing of later component tags)."""
      fences = sum(1 for l in text.split("\n") if l.lstrip().startswith("```"))
      if fences % 2:
          text += "\n```"
      return text


  def docstring_md(text):
      return close_dangling_fences(convert_google_sections(clean_docstring(text)))
%>

<%def name="signature_block(kind, name, params, returns, refname)" buffered="True">
<ApiSignature>

```python
${format_signature(kind, name, params, returns)}
```

</ApiSignature>
</%def>

<%def name="function(func, depth)" buffered="True">
<%
    returns = show_type_annotations and func.return_annotation() or ''
    if returns:
        returns = ' -> ' + returns
    params = func.params(annotate=show_type_annotations)
    heading = '#' * depth
    kind = "method" if func.cls else "function"
%>
${heading} `${func.name}` {#${func.refname}}

<ApiMember kind="${kind}">

${signature_block('def', func.name, params, returns, func.refname)}
${docstring_md(func.docstring)}

</ApiMember>
</%def>

<%def name="variable(var, depth)" buffered="True">
<%
    annot = show_type_annotations and var.type_annotation() or ''
    if annot:
        annot = ': ' + annot
    doc = docstring_md(var.docstring)
    doc_lines = ["  " + l if l.strip() else "" for l in doc.split("\n")] if doc else []
%>
- **`${var.name}`**${annot and ("&nbsp;(`%s`)" % annot[2:]) or ''}
% if doc_lines:

${"\n".join(doc_lines)}
% endif
</%def>

<%def name="class_(cls, depth)" buffered="True">
<%
  params = cls.params(annotate=show_type_annotations)
  class_vars = [v for v in cls.class_variables(show_inherited_members, sort=sort_identifiers)
                if v.name not in PYDANTIC_NOISE_MEMBERS]
  static_methods = [f for f in cls.functions(show_inherited_members, sort=sort_identifiers)
                    if f.name not in PYDANTIC_NOISE_MEMBERS]
  inst_vars = [v for v in cls.instance_variables(show_inherited_members, sort=sort_identifiers)
               if v.name not in PYDANTIC_NOISE_MEMBERS]
  methods = [m for m in cls.methods(show_inherited_members, sort=sort_identifiers)
             if m.name not in PYDANTIC_NOISE_MEMBERS]
  mro = [c for c in cls.mro() if c.refname not in ("pydantic.main.BaseModel", "builtins.object")]
  # cls.obj can be a typing generic alias (e.g. a Callable type alias) rather
  # than a real class, for which pdoc3's subclasses() raises TypeError.
  try:
      subclasses = cls.subclasses()
  except TypeError:
      subclasses = []
  heading = '#' * depth
  sub = '#' * (depth + 1)
%>
${heading} `${cls.name}` {#${cls.refname}}

<ApiMember kind="class">

${signature_block('class', cls.name, params, '', cls.refname)}
${docstring_md(cls.docstring)}

% if mro:
**Bases:** ${", ".join("`%s`" % c.refname for c in mro)}

% endif
% if subclasses:
**Subclasses:** ${", ".join("`%s`" % c.refname for c in subclasses)}

% endif
% if class_vars or inst_vars:
${sub} Attributes {#${cls.refname}--attributes}

% for v in class_vars:
${variable(v, depth + 1)}
% endfor
% for v in inst_vars:
${variable(v, depth + 1)}
% endfor

% endif
% for f in static_methods:
${function(f, depth + 1)}
% endfor
% for m in methods:
${function(m, depth + 1)}
% endfor

</ApiMember>
</%def>

## Start the output logic for an entire module.

<%
  variables = module.variables(sort=sort_identifiers)
  classes = module.classes(sort=sort_identifiers)
  functions = module.functions(sort=sort_identifiers)
  submodules = module.submodules()
%>

${docstring_md(module.docstring)}

% if submodules:
## Submodules

% for m in submodules:
- `${m.name}`
% endfor

% endif
% if variables:
## Variables

% for v in variables:
${variable(v, 2)}
% endfor

% endif
% if functions:
## Functions

% for f in functions:
${function(f, 3)}
% endfor
% endif
% if classes:
## Classes

% for c in classes:
${class_(c, 3)}
% endfor
% endif
