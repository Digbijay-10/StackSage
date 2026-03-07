import * as vscode from 'vscode';
import fetch from 'node-fetch';

const API_KEY = "";

export function activate(context: vscode.ExtensionContext) {

	const disposable = vscode.commands.registerCommand('pyweb-doctor.fixCode', async () => {

		const editor = vscode.window.activeTextEditor;

		if (!editor) {
			vscode.window.showInformationMessage('No editor');
			return;
		}

		let selection = editor.selection;
		let text = editor.document.getText(selection);

		// if nothing selected → use current line
		if (!text) {

			const line = editor.selection.active.line;

			const lineRange = editor.document.lineAt(line).range;

			selection = new vscode.Selection(
				lineRange.start,
				lineRange.end
			);

			text = editor.document.getText(selection);

		}

		if (!text) {
			vscode.window.showInformationMessage('No code found');
			return;
		}

		const prompt =
"Fix the code below. Return ONLY the corrected code. Do not use markdown. Do not use ``` . Do not explain.\n\n" + text;

		try {

			const res = await fetch(
				`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${API_KEY}`,
				{
					method: "POST",
					headers: {
						"Content-Type": "application/json"
					},
					body: JSON.stringify({
						contents: [
							{
								parts: [
									{ text: prompt }
								]
							}
						]
					})
				}
			);

			const data: any = await res.json();

			const reply =
				data.candidates?.[0]?.content?.parts?.[0]?.text ||
				"No response";


			editor.edit(editBuilder => {
				editBuilder.replace(selection, reply);
			});


		} catch (e) {

			vscode.window.showErrorMessage("Gemini error");

		}

	});

	context.subscriptions.push(disposable);
}

export function deactivate() {}