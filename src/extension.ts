import * as vscode from 'vscode';
import fetch from 'node-fetch';

let panel: vscode.WebviewPanel | undefined;

export function activate(context: vscode.ExtensionContext) {


	// =========================
	// FIX CODE
	// =========================

	const fixCmd = vscode.commands.registerCommand(
		'pyweb-doctor.fixCode',
		async () => {

			const editor = vscode.window.activeTextEditor;

			if (!editor) {
				vscode.window.showInformationMessage('No editor');
				return;
			}

			let selection = editor.selection;
			let text = editor.document.getText(selection);

			if (!text) {

				const fullRange = new vscode.Range(
					editor.document.positionAt(0),
					editor.document.positionAt(editor.document.getText().length)
				);

				selection = new vscode.Selection(
					fullRange.start,
					fullRange.end
				);

				text = editor.document.getText(selection);

			}

			if (!text) {
				vscode.window.showInformationMessage('No code found');
				return;
			}

			try {

				const res = await fetch(
					"http://127.0.0.1:8080/fix",
					{
						method: "POST",
						headers: {
							"Content-Type": "application/json"
						},
						body: JSON.stringify({
							code: text
						})
					}
				);

				const data: any = await res.json();

				const reply = data.result || "";

				await editor.edit(editBuilder => {
					editBuilder.replace(selection, reply);
				});

			} catch {

				vscode.window.showErrorMessage("Backend not running");

			}

		}
	);

	context.subscriptions.push(fixCmd);



	// =========================
	// REVERSE DEBUG
	// =========================

	const reverseCmd = vscode.commands.registerCommand(
		'pyweb-doctor.reverseDebug',
		async () => {

			const editor = vscode.window.activeTextEditor;

			if (!editor) {
				vscode.window.showInformationMessage('No editor');
				return;
			}

			const code = editor.document.getText();

			if (!code) {
				vscode.window.showInformationMessage('No code found');
				return;
			}

			const expected = await vscode.window.showInputBox({
				prompt: "Enter expected output"
			});

			if (!expected) {
				return;
			}

			try {

				const res = await fetch(
					"http://127.0.0.1:8080/reverse",
					{
						method: "POST",
						headers: {
							"Content-Type": "application/json"
						},
						body: JSON.stringify({
							code: code,
							expected: expected
						})
					}
				);

				const data: any = await res.json();

				const fixed = data.fixed || "";
				const explanation = data.explanation || "";

				const fullRange = new vscode.Range(
					editor.document.positionAt(0),
					editor.document.positionAt(editor.document.getText().length)
				);

				await editor.edit(editBuilder => {
					editBuilder.replace(fullRange, fixed);
				});

				if (!panel) {

					panel = vscode.window.createWebviewPanel(
						'pywebDoctor',
						'PyWeb Doctor',
						vscode.ViewColumn.Beside,
						{ enableScripts: true }
					);

					panel.onDidDispose(() => {
						panel = undefined;
					});

				}

				panel.webview.html = `
				<html>
				<body style="font-family:sans-serif;padding:10px;">
				<h2>Reverse Debug</h2>
				<pre>${explanation}</pre>
				</body>
				</html>
				`;

			} catch {

				vscode.window.showErrorMessage("Reverse debug failed");

			}

		}
	);

	context.subscriptions.push(reverseCmd);



	// =========================
	// EXPLAIN
	// =========================

	const explainCmd = vscode.commands.registerCommand(
		'pyweb-doctor.showExplanation',
		async () => {

			const editor = vscode.window.activeTextEditor;

			if (!editor) {
				vscode.window.showInformationMessage('No editor');
				return;
			}

			const code = editor.document.getText();

			if (!code) {
				vscode.window.showInformationMessage('No code found');
				return;
			}

			try {

				const res = await fetch(
					"http://127.0.0.1:8080/explain",
					{
						method: "POST",
						headers: {
							"Content-Type": "application/json"
						},
						body: JSON.stringify({
							code: code,
							error: ""
						})
					}
				);

				const data: any = await res.json();

				const explanation = data.explanation || "No explanation";


				if (!panel) {

					panel = vscode.window.createWebviewPanel(
						'pywebDoctor',
						'PyWeb Doctor',
						vscode.ViewColumn.Beside,
						{ enableScripts: true }
					);

					panel.onDidDispose(() => {
						panel = undefined;
					});

				}


				panel.webview.html = `
				<html>
				<body style="font-family:sans-serif;padding:10px;">

				<h2>Explanation</h2>

				<div style="
				background:#1e1e1e;
				color:#ddd;
				padding:10px;
				border-radius:6px;
				white-space:pre-wrap;
				">

				${explanation}

				</div>

				</body>
				</html>
				`;

			} catch {

				vscode.window.showErrorMessage("Explain failed");

			}

		}
	);

	context.subscriptions.push(explainCmd);

}

export function deactivate() { }