from __future__ import annotations

import ast
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class PythonSymbol:
    name: str
    qualified_name: str
    kind: str
    path: str
    line: int
    end_line: int
    signature: str
    docstring: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class _SymbolVisitor(ast.NodeVisitor):
    def __init__(self, path: str) -> None:
        self.path = path
        self.scope: list[str] = []
        self.symbols: list[PythonSymbol] = []
        self.imports: list[dict[str, Any]] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._add(node, "class", self._class_signature(node))
        self.scope.append(node.name)
        self.generic_visit(node)
        self.scope.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        kind = "method" if self.scope else "function"
        self._add(node, kind, self._function_signature(node))
        self.scope.append(node.name)
        self.generic_visit(node)
        self.scope.pop()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        kind = "async_method" if self.scope else "async_function"
        self._add(node, kind, "async " + self._function_signature(node))
        self.scope.append(node.name)
        self.generic_visit(node)
        self.scope.pop()

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self.imports.append(
                {"module": alias.name, "name": None, "alias": alias.asname, "line": node.lineno}
            )

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        module = "." * node.level + (node.module or "")
        for alias in node.names:
            self.imports.append(
                {"module": module, "name": alias.name, "alias": alias.asname, "line": node.lineno}
            )

    def _add(
        self, node: ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef, kind: str, signature: str
    ) -> None:
        qualified = ".".join([*self.scope, node.name])
        docstring = ast.get_docstring(node, clean=True) or ""
        self.symbols.append(
            PythonSymbol(
                name=node.name,
                qualified_name=qualified,
                kind=kind,
                path=self.path,
                line=node.lineno,
                end_line=getattr(node, "end_lineno", node.lineno),
                signature=signature,
                docstring=docstring[:500],
            )
        )

    @staticmethod
    def _function_signature(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
        try:
            arguments = ast.unparse(node.args)
        except (AttributeError, ValueError):
            arguments = "..."
        returns = f" -> {ast.unparse(node.returns)}" if node.returns is not None else ""
        return f"{node.name}({arguments}){returns}"

    @staticmethod
    def _class_signature(node: ast.ClassDef) -> str:
        bases = [ast.unparse(base) for base in node.bases]
        return f"class {node.name}" + (f"({', '.join(bases)})" if bases else "")


def inspect_python_file(path: Path, relative: str, max_file_bytes: int) -> dict[str, Any]:
    if path.stat().st_size > max_file_bytes:
        return {"path": relative, "symbols": [], "imports": [], "error": "file too large"}
    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=relative)
    except (OSError, UnicodeDecodeError, SyntaxError) as exc:
        return {"path": relative, "symbols": [], "imports": [], "error": str(exc)}
    visitor = _SymbolVisitor(relative)
    visitor.visit(tree)
    return {
        "path": relative,
        "symbols": [symbol.to_dict() for symbol in visitor.symbols],
        "imports": visitor.imports,
        "error": None,
    }


def iter_python_files(root: Path, skip_dirs: set[str]) -> list[Path]:
    paths: list[Path] = []
    for current, dirs, files in os.walk(root):
        dirs[:] = sorted(item for item in dirs if item not in skip_dirs)
        paths.extend(Path(current) / name for name in sorted(files) if name.endswith(".py"))
    return paths
