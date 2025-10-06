<!DOCTYPE html>
<html>
<head>
	<meta http-equiv="content-type" content="text/html; charset=utf-8"/>
	<title></title>
	<meta name="generator" content="LibreOffice 24.2.4.2 (Windows)"/>
	<meta name="created" content="2025-10-06T09:19:36.248000000"/>
	<meta name="changed" content="2025-10-06T09:29:13.104000000"/>
	<style type="text/css">
		@page { size: 8.27in 11.69in; margin: 0.79in }
		p { line-height: 115%; margin-bottom: 0.1in; background: transparent }
		h3 { margin-top: 0.1in; margin-bottom: 0.08in; background: transparent; page-break-after: avoid }
		h3.western { font-family: "Liberation Serif", serif; font-size: 14pt; font-weight: bold }
		h3.cjk { font-family: "NSimSun"; font-size: 14pt; font-weight: bold }
		h3.ctl { font-family: "Arial"; font-size: 14pt; font-weight: bold }
		strong { font-weight: bold }
		code.western { font-family: "Liberation Mono", monospace }
		code.cjk { font-family: "NSimSun", monospace }
		code.ctl { font-family: "Liberation Mono", monospace }
		a:link { color: #000080; text-decoration: underline }
	</style>
</head>
<body lang="en-US" link="#000080" vlink="#800000" dir="ltr"><h3 class="western">
<strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">Manual
for:&nbsp;</span></span></span></font></font></span></strong><span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><strong><span style="font-variant: normal"><font color="#000000"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">mcp.py</span></span></span></font></font></font></span></strong></span><strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">&nbsp;(Master
Control Program)</span></span></span></font></font></span></strong></h3>
<p style="line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.19in">
<strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">1.
Purpose</span></span></span></font></font></font></span></strong></p>
<p style="line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.19in">
<span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">The&nbsp;</span></span></span></font></font></font></span><strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">Master
Control Program (MCP)</span></span></span></font></font></font></span></strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">&nbsp;is
the central &quot;brain&quot; of the entire AI system. It acts as an
intelligent orchestrator, receiving input from various sources (like
chat, audio, or a vision system), deciding how to process that input,
and then dispatching tasks to the appropriate services.</span></span></span></font></font></font></span></p>
<p style="font-variant: normal; letter-spacing: normal; font-style: normal; font-weight: normal; line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.19in">
<font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt">Its
primary goal is to understand user requests, enrich them with
contextual information (like what the camera sees), get a meaningful
response from a powerful Large Language Model (LLM), and then
broadcast that response to output channels like a Text-to-Speech
(TTS) engine or a social media live stream.</font></font></font></p>
<p style="line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.19in">
<strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">2.
Features</span></span></span></font></font></font></span></strong></p>
<ul>
	<li><p style="line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.03in; border: none; padding: 0in">
	<strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">Unified
	Server Architecture:</span></span></span></font></font></font></span></strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">&nbsp;Provides
	a single, centralized Flask web server to handle requests from all
	other scripts.</span></span></span></font></font></font></span></p></li>
	<li><p style="line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.03in; border: none; padding: 0in">
	<strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">Multi-LLM
	Support:</span></span></span></font></font></font></span></strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">&nbsp;Can
	be configured to use either&nbsp;</span></span></span></font></font></font></span><strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">Google's
	Gemini</span></span></span></font></font></font></span></strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">&nbsp;or
	a local&nbsp;</span></span></span></font></font></font></span><strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">Ollama</span></span></span></font></font></font></span></strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">&nbsp;model
	as its core reasoning engine.</span></span></span></font></font></font></span></p></li>
	<li><p style="line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.03in; border: none; padding: 0in">
	<strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">Wake
	Word Detection:</span></span></span></font></font></font></span></strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">&nbsp;Ignores
	all input unless it begins with a configured &quot;wake word&quot;
	(e.g., &quot;computer,&quot; &quot;assistant&quot;), preventing it
	from responding to unintended chatter.</span></span></span></font></font></font></span></p></li>
	<li><p style="line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.03in; border: none; padding: 0in">
	<strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">Intelligent
	Vision Integration:</span></span></span></font></font></font></span></strong></p>
	<ul>
		<li><p style="font-variant: normal; letter-spacing: normal; font-style: normal; font-weight: normal; line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.03in; border: none; padding: 0in">
		<font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt">Uses
		a cached &quot;memory&quot; of the last thing it saw to answer
		questions without needing a new scan every time.</font></font></font></p></li>
		<li><p style="font-variant: normal; letter-spacing: normal; font-style: normal; font-weight: normal; line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.03in; border: none; padding: 0in">
		<font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt">Automatically
		requests a fresh scan from the&nbsp;<span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt">vision.py</font></font></span>&nbsp;service
		when it detects vision-related keywords (e.g., &quot;look,&quot;
		&quot;see,&quot; &quot;what is that&quot;).</font></font></font></p></li>
	</ul>
	<li><p style="line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.03in; border: none; padding: 0in">
	<strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">Intent
	Recognition:</span></span></span></font></font></font></span></strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">&nbsp;Differentiates
	between a general&nbsp;</span></span></span></font></font></font></span><strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">question</span></span></span></font></font></font></span></strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">&nbsp;and
	a direct&nbsp;</span></span></span></font></font></font></span><strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">command</span></span></span></font></font></font></span></strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">&nbsp;to
	provide better-formatted prompts to the LLM.</span></span></span></font></font></font></span></p></li>
	<li><p style="line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.03in; border: none; padding: 0in">
	<strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">External
	Service Integration:</span></span></span></font></font></font></span></strong></p>
	<ul>
		<li><p style="line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.03in; border: none; padding: 0in">
		<strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">Vision
		Service:</span></span></span></font></font></font></span></strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">&nbsp;Can
		command the vision script to perform a visual scan.</span></span></span></font></font></font></span></p></li>
		<li><p style="line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.03in; border: none; padding: 0in">
		<strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">StyleTTS:</span></span></span></font></font></font></span></strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">&nbsp;Sends
		final responses to a TTS server to be spoken aloud.</span></span></span></font></font></font></span></p></li>
		<li><p style="line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.03in; border: none; padding: 0in">
		<strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">Social
		Stream Ninja:</span></span></span></font></font></font></span></strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">&nbsp;Pushes
		final responses to a live streaming overlay.</span></span></span></font></font></font></span></p></li>
	</ul>
	<li><p style="line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.03in; border: none; padding: 0in">
	<strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">Response
	Management:</span></span></span></font></font></font></span></strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">&nbsp;Can
	truncate long LLM responses to a configured maximum length to keep
	them concise.</span></span></span></font></font></font></span></p></li>
</ul>
<p style="line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.19in">
<strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">3.
How it Works</span></span></span></font></font></font></span></strong></p>
<p style="font-variant: normal; letter-spacing: normal; font-style: normal; font-weight: normal; line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.19in">
<font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt">The
MCP operates as a continuous web service. The typical workflow for a
request is as follows:</font></font></font></p>
<ol>
	<li><p style="font-variant: normal; letter-spacing: normal; font-style: normal; font-weight: normal; line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.03in; border: none; padding: 0in">
	<font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt">An
	external service (e.g., an audio transcriber) sends a user's text to
	one of MCP's API endpoints (like&nbsp;<span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt">/audio</font></font></span>).</font></font></font></p></li>
	<li><p style="font-variant: normal; letter-spacing: normal; font-style: normal; font-weight: normal; line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.03in; border: none; padding: 0in">
	<font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt">The
	request is routed to the central&nbsp;<span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt">process_task()</font></font></span>&nbsp;function.</font></font></font></p></li>
	<li><p style="line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.03in; border: none; padding: 0in">
	<span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">The
	function first checks if the user's text starts with a valid&nbsp;</span></span></span></font></font></font></span><strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">wake
	word</span></span></span></font></font></font></span></strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">.
	If not, it ignores the request.</span></span></span></font></font></font></span></p></li>
	<li><p style="line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.03in; border: none; padding: 0in">
	<span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">If
	a wake word is present, it determines the necessary&nbsp;</span></span></span></font></font></font></span><strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">visual
	context</span></span></span></font></font></font></span></strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">.
	If the request came from the vision service, it uses the fresh
	context provided. If not, it checks for trigger words; if found, it
	calls the&nbsp;</span></span></span></font></font></font></span><span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><span style="font-variant: normal"><font color="#000000"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">vision.py</span></span></span></font></font></font></span></span><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">&nbsp;service
	for a new scan. Otherwise, it uses its cached visual memory.</span></span></span></font></font></font></span></p></li>
	<li><p style="line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.03in; border: none; padding: 0in">
	<span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">It
	constructs a detailed&nbsp;</span></span></span></font></font></font></span><strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">prompt</span></span></span></font></font></font></span></strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">&nbsp;for
	the LLM, combining the user's text and the visual context.</span></span></span></font></font></font></span></p></li>
	<li><p style="font-variant: normal; letter-spacing: normal; font-style: normal; font-weight: normal; line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.03in; border: none; padding: 0in">
	<font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt">The
	prompt is sent to the configured LLM (Gemini or Ollama).</font></font></font></p></li>
	<li><p style="font-variant: normal; letter-spacing: normal; font-style: normal; font-weight: normal; line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.03in; border: none; padding: 0in">
	<font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt">The
	LLM's raw response is received, cleaned up, and truncated if
	necessary.</font></font></font></p></li>
	<li><p style="font-variant: normal; letter-spacing: normal; font-style: normal; font-weight: normal; line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.03in; border: none; padding: 0in">
	<font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt">This
	final, polished response is then sent to the StyleTTS service (to be
	spoken) and the Social Stream Ninja service (to be displayed).</font></font></font></p></li>
	<li><p style="font-variant: normal; letter-spacing: normal; font-style: normal; font-weight: normal; line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.03in; border: none; padding: 0in">
	<font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt">A
	confirmation response is sent back to the service that made the
	original request.</font></font></font></p></li>
</ol>
<p style="line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.19in">
<strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">4.
Setup &amp; Installation</span></span></span></font></font></font></span></strong></p>
<ul>
	<li><p style="line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.03in; border: none; padding: 0in">
	<strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">Dependencies:</span></span></span></font></font></font></span></strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">&nbsp;You
	must have the required Python libraries installed. You can install
	them all with the following command:</span></span></span></font></font></font></span></p>
	<p style="font-variant: normal; letter-spacing: normal; font-style: normal; font-weight: normal; line-height: 100%; orphans: 2; widows: 2; margin-bottom: 0in; border: none; padding: 0in">
	<font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><font face="Google Symbols"><font size="4" style="font-size: 13pt">code</font></font>Bash</font></font></font></p></li>
	<li><p align="center" style="line-height: 100%; margin-bottom: 0in"><font size="4" style="font-size: 14pt"><b>!!
	OBS USE PYTHON 3.10 THIS IS REQUIRED FOR FLASH-ATTN2 !!</b></font></p></li>
	<li><p align="center" style="line-height: 100%; margin-bottom: 0in"><font size="3" style="font-size: 12pt">You
	can compile your own wheel but I use the wheel from this link</font></p></li>
	<li><p align="center" style="line-height: 100%; margin-bottom: 0in"><font size="3" style="font-size: 12pt"><a href="https://github.com/sunsetcoder/flash-attention-windows">https://github.com/sunsetcoder/flash-attention-windows</a></font></p></li>
</ul>
<div id="cdk-accordion-child-24" dir="ltr">
	<ul><li><p style="line-height: 100%; margin-bottom: 0in"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt">cd
		C:\Users\jorge\Documents\AI\gem-system</font></font></p></li>
		<li><p style="line-height: 100%; margin-bottom: 0in"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt">conda
		create --name mcp_env<span lang="sv-SE">_1</span> python=3.10 -y</font></font></p></li>
		<li><p style="line-height: 100%; margin-bottom: 0in"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt">conda
		activate mcp_env<span lang="sv-SE">_1</span></font></font></p></li>
		<li><p style="line-height: 100%; margin-bottom: 0in"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt">pip
		install Flask Flask-Cors google-generativeai requests </font></font>
		</p></li>
		<li><p style="line-height: 100%; margin-bottom: 0in"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt">pip
		install opencv-python Pillow </font></font>
		</p></li>
		<li><p style="line-height: 100%; margin-bottom: 0in"><font color="#ff0000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt">#
		torch torchvision This depends on your cuda version </font></font></font>
		</p></li>
		<li><p style="line-height: 100%; margin-bottom: 0in"><font color="#ff0000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt">#
		Use nvcc –version to get the cuda version you have installed.</font></font></font></p></li>
		<li><p style="line-height: 100%; margin-bottom: 0in"><font color="#ff0000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt">#
		Then go to <a href="https://pytorch.org/get-started/locally/">https://pytorch.org/get-started/locally/</a>
		to get the command to run.</font></font></font></p></li>
		<li><p style="line-height: 100%; margin-bottom: 0in"><font color="#ff0000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt">#
		For my set up the install command is</font></font></font></p></li>
		<li><p style="line-height: 100%; margin-bottom: 0in"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt">pip3
		install torch torchvision --index-url
		https://download.pytorch.org/whl/cu128</font></font></p></li>
		<li><p style="line-height: 100%; margin-bottom: 0in"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt">pip3
		install  torchaudio</font></font></p></li>
		<li><p style="line-height: 100%; margin-bottom: 0in"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt">pip3
		 install transformers</font></font></p></li>
		<li><p style="line-height: 100%; margin-bottom: 0in"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt">pip3
		 install accelerate</font></font></p></li>
		<li><p style="line-height: 100%; margin-bottom: 0in"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt">pip
		install sounddevice webrtcvad scipy </font></font>
		</p></li>
		<li><p style="line-height: 100%; margin-bottom: 0in"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt">pip
		install python-osc</font></font></p></li>
		<li><p style="line-height: 100%; margin-bottom: 0in"><code class="western"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt">pip
		install opencv-python</font></font></code></p></li>
		<li><p style="line-height: 100%; margin-bottom: 0in"><code class="western"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt">pip
		install ninja </font></font></code>
		</p></li>
	</ul>
</div>
<ul>
	<li><p style="line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.03in; border: none; padding: 0in">
	<strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">Configuration
	(</span></span></span></font></font></font></span></strong><span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">mcp_settings.ini</span></span></span></font></font></font></span></strong></span><strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">):</span></span></span></font></font></font></span></strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">&nbsp;This
	file is&nbsp;</span></span></span></font></font></font></span><strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">critical</span></span></span></font></font></font></span></strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">&nbsp;for
	the MCP's operation. It must be in the same directory as the script.
	Below is a description of each setting:</span></span></span></font></font></font></span></p>
	<ul>
		<li><p style="line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.03in; border: none; padding: 0in">
		<span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><strong><span style="font-variant: normal"><font color="#000000"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">[MCP]</span></span></span></font></font></font></span></strong></span></p>
		<ul>
			<li><p style="font-variant: normal; letter-spacing: normal; font-style: normal; font-weight: normal; line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.03in; border: none; padding: 0in">
			<span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt">llm_choice</font></font></span>:
			The core LLM to use. Must be either&nbsp;<span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt">gemini</font></font></span>&nbsp;or&nbsp;<span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt">ollama</font></font></span>.</font></font></font></p></li>
			<li><p style="font-variant: normal; letter-spacing: normal; font-style: normal; font-weight: normal; line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.03in; border: none; padding: 0in">
			<span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt">host</font></font></span>:
			The IP address for the server to run on (e.g.,&nbsp;<span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt">127.0.0.1</font></font></span>&nbsp;for
			local only,&nbsp;<span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt">0.0.0.0</font></font></span>&nbsp;for
			network access).</font></font></font></p></li>
			<li><p style="font-variant: normal; letter-spacing: normal; font-style: normal; font-weight: normal; line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.03in; border: none; padding: 0in">
			<span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt">port</font></font></span>:
			The port for the server (e.g.,&nbsp;<span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt">5000</font></font></span>).</font></font></font></p></li>
		</ul>
		<li><p style="line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.03in; border: none; padding: 0in">
		<span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><strong><span style="font-variant: normal"><font color="#000000"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">[Assistant]</span></span></span></font></font></font></span></strong></span></p>
		<ul>
			<li><p style="font-variant: normal; letter-spacing: normal; font-style: normal; font-weight: normal; line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.03in; border: none; padding: 0in">
			<span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt">max_response_length</font></font></span>:
			The maximum number of characters for the final response. Set
			to&nbsp;<span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt">0</font></font></span>&nbsp;to
			disable truncation.</font></font></font></p></li>
			<li><p style="font-variant: normal; letter-spacing: normal; font-style: normal; font-weight: normal; line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.03in; border: none; padding: 0in">
			<span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt">wake_words</font></font></span>:
			A comma-separated list of words that the assistant will respond to
			(e.g.,&nbsp;<span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt">computer,
			assistant, jarvis</font></font></span>).</font></font></font></p></li>
			<li><p style="font-variant: normal; letter-spacing: normal; font-style: normal; font-weight: normal; line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.03in; border: none; padding: 0in">
			<span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt">command_verbs</font></font></span>:
			A comma-separated list of words that indicate the user is giving a
			command (e.g.,&nbsp;<span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt">go
			to, open, start</font></font></span>).</font></font></font></p></li>
		</ul>
		<li><p style="line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.03in; border: none; padding: 0in">
		<span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><strong><span style="font-variant: normal"><font color="#000000"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">[VisionService]</span></span></span></font></font></font></span></strong></span></p>
		<ul>
			<li><p style="font-variant: normal; letter-spacing: normal; font-style: normal; font-weight: normal; line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.03in; border: none; padding: 0in">
			<span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt">scan_url</font></font></span>:
			The full URL to the vision service's scan endpoint
			(e.g.,&nbsp;<span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt">http://127.0.0.1:5001/scan</font></font></span>).</font></font></font></p></li>
			<li><p style="font-variant: normal; letter-spacing: normal; font-style: normal; font-weight: normal; line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.03in; border: none; padding: 0in">
			<span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt">vision_trigger_words</font></font></span>:
			Comma-separated words that trigger a new vision scan (e.g.,&nbsp;<span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt">look,
			see, what do you see, analyze</font></font></span>).</font></font></font></p></li>
		</ul>
		<li><p style="line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.03in; border: none; padding: 0in">
		<span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><strong><span style="font-variant: normal"><font color="#000000"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">[SocialStream]</span></span></span></font></font></font></span></strong></span></p>
		<ul>
			<li><p style="font-variant: normal; letter-spacing: normal; font-style: normal; font-weight: normal; line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.03in; border: none; padding: 0in">
			<span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt">enabled</font></font></span>:
			Set to&nbsp;<span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt">true</font></font></span>&nbsp;or&nbsp;<span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt">false</font></font></span>&nbsp;to
			enable/disable integration.</font></font></font></p></li>
			<li><p style="font-variant: normal; letter-spacing: normal; font-style: normal; font-weight: normal; line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.03in; border: none; padding: 0in">
			<span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt">session_id</font></font></span>,&nbsp;<span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt">target_platform</font></font></span>,&nbsp;<span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt">api_url</font></font></span>:
			Settings specific to your Social Stream Ninja setup.</font></font></font></p></li>
		</ul>
		<li><p style="line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.03in; border: none; padding: 0in">
		<span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><strong><span style="font-variant: normal"><font color="#000000"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">[StyleTTS]</span></span></span></font></font></font></span></strong></span></p>
		<ul>
			<li><p style="font-variant: normal; letter-spacing: normal; font-style: normal; font-weight: normal; line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.03in; border: none; padding: 0in">
			<span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt">enabled</font></font></span>:
			Set to&nbsp;<span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt">true</font></font></span>&nbsp;or&nbsp;<span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt">false</font></font></span>&nbsp;to
			enable/disable integration.</font></font></font></p></li>
			<li><p style="font-variant: normal; letter-spacing: normal; font-style: normal; font-weight: normal; line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.03in; border: none; padding: 0in">
			<span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt">tts_url</font></font></span>:
			The URL for your StyleTTS server's endpoint.</font></font></font></p></li>
		</ul>
		<li><p style="line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.03in; border: none; padding: 0in">
		<span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><strong><span style="font-variant: normal"><font color="#000000"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">[Gemini]</span></span></span></font></font></font></span></strong></span></p>
		<ul>
			<li><p style="line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.03in; border: none; padding: 0in">
			<span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><span style="font-variant: normal"><font color="#000000"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">api_key</span></span></span></font></font></font></span></span><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">:&nbsp;</span></span></span></font></font></font></span><strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">Required
			if&nbsp;</span></span></span></font></font></font></span></strong><span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><strong><span style="font-variant: normal"><font color="#000000"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">llm_choice</span></span></span></font></font></font></span></strong></span><strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">&nbsp;is&nbsp;</span></span></span></font></font></font></span></strong><span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><strong><span style="font-variant: normal"><font color="#000000"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">gemini</span></span></span></font></font></font></span></strong></span><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">.
			Your Google AI Studio API key.</span></span></span></font></font></font></span></p></li>
			<li><p style="font-variant: normal; letter-spacing: normal; font-style: normal; font-weight: normal; line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.03in; border: none; padding: 0in">
			<span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt">model</font></font></span>:
			The specific Gemini model to use (e.g.,&nbsp;<span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt">gemini-1.5-flash</font></font></span>).</font></font></font></p></li>
		</ul>
		<li><p style="line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.03in; border: none; padding: 0in">
		<span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><strong><span style="font-variant: normal"><font color="#000000"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">[Ollama]</span></span></span></font></font></font></span></strong></span></p>
		<ul>
			<li><p style="line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.03in; border: none; padding: 0in">
			<span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><span style="font-variant: normal"><font color="#000000"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">model</span></span></span></font></font></font></span></span><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">:&nbsp;</span></span></span></font></font></font></span><strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">Required
			if&nbsp;</span></span></span></font></font></font></span></strong><span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><strong><span style="font-variant: normal"><font color="#000000"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">llm_choice</span></span></span></font></font></font></span></strong></span><strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">&nbsp;is&nbsp;</span></span></span></font></font></font></span></strong><span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><strong><span style="font-variant: normal"><font color="#000000"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">ollama</span></span></span></font></font></font></span></strong></span><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">.
			The name of the Ollama model (e.g.,&nbsp;</span></span></span></font></font></font></span><span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><span style="font-variant: normal"><font color="#000000"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">llama3:instruct</span></span></span></font></font></font></span></span><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">).</span></span></span></font></font></font></span></p></li>
			<li><p style="font-variant: normal; letter-spacing: normal; font-style: normal; font-weight: normal; line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.03in; border: none; padding: 0in">
			<span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt">api_url</font></font></span>:
			The URL to the Ollama chat API endpoint
			(e.g.,&nbsp;<span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt">http://localhost:11434/api/chat</font></font></span>).</font></font></font></p></li>
		</ul>
	</ul>
</ul>
<p style="line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.19in">
<strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">5.
Usage</span></span></span></font></font></font></span></strong></p>
<ul>
	<li><p style="line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.03in; border: none; padding: 0in">
	<strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">Running
	the Script:</span></span></span></font></font></font></span></strong></p>
	<ol>
		<li><p style="font-variant: normal; letter-spacing: normal; font-style: normal; font-weight: normal; line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.03in; border: none; padding: 0in">
		<font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt">Ensure
		your&nbsp;<span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt">mcp_settings.ini</font></font></span>&nbsp;file
		is correctly configured.</font></font></font></p></li>
		<li><p style="font-variant: normal; letter-spacing: normal; font-style: normal; font-weight: normal; line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.03in; border: none; padding: 0in">
		<font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt">Run
		the script from your terminal:</font></font></font></p>
		<p style="font-variant: normal; letter-spacing: normal; font-style: normal; font-weight: normal; line-height: 100%; orphans: 2; widows: 2; margin-bottom: 0in; border: none; padding: 0in">
		<font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><font face="Google Symbols"><font size="4" style="font-size: 13pt">code</font></font>Bash</font></font></font></p></li>
	</ol>
</ul>
<div id="cdk-accordion-child-25" dir="ltr">
	<ul>
		<ol start="2"><li style="display: block"><p style="line-height: 100%; margin-bottom: 0in">
			<code class="western"><font face="Inter, sans-serif"><font size="2" style="font-size: 9pt"><span lang="sv-SE">Cd
			…….\gem-system</span></font></font></code></p></li>
			<li><p style="line-height: 100%; margin-bottom: 0in"><code class="western"><font face="Inter, sans-serif"><font size="2" style="font-size: 9pt"><span lang="sv-SE">c</span></font></font></code><code class="western"><font face="Inter, sans-serif"><font size="2" style="font-size: 9pt">onda
			activate mcp_env</font></font></code><code class="western"><font face="Inter, sans-serif"><font size="2" style="font-size: 9pt"><span lang="sv-SE">_1</span></font></font></code></p></li>
			<li><p style="line-height: 100%; margin-bottom: 0in"><code class="western"><font face="Inter, sans-serif"><font size="2" style="font-size: 9pt">python
			mcp.py</font></font></code></p></li>
		</ol>
	</ul>
</div>
<ul>
	<ol start="5">
		<li><p style="font-variant: normal; letter-spacing: normal; font-style: normal; font-weight: normal; line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.03in; border: none; padding: 0in">
		<font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt">The
		server will start and print the address it is listening on.</font></font></font></p></li>
	</ol>
	<li><p style="line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.03in; border: none; padding: 0in">
	<strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">API
	Endpoints:</span></span></span></font></font></font></span></strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">&nbsp;The
	MCP is controlled by sending HTTP requests to its endpoints.</span></span></span></font></font></font></span></p>
	<ol>
		<li><p style="line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.03in; border: none; padding: 0in">
		<span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><strong><span style="font-variant: normal"><font color="#000000"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">/chat</span></span></span></font></font></font></span></strong></span><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">&nbsp;(POST,
		PUT)</span></span></span></font></font></font></span></p>
		<ul>
			<li><p style="line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.03in; border: none; padding: 0in">
			<strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">Purpose:</span></span></span></font></font></font></span></strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">&nbsp;To
			process input from a text-based chat interface.</span></span></span></font></font></font></span></p></li>
			<li><p style="line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.03in; border: none; padding: 0in">
			<strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">Payload:</span></span></span></font></font></font></span></strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">&nbsp;</span></span></span></font></font></font></span><span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><span style="font-variant: normal"><font color="#000000"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">{&quot;chatmessage&quot;:
			&quot;your message here&quot;}</span></span></span></font></font></font></span></span></p></li>
			<li><p style="line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.03in; border: none; padding: 0in">
			<strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">Returns:</span></span></span></font></font></font></span></strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">&nbsp;</span></span></span></font></font></font></span><span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><span style="font-variant: normal"><font color="#000000"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">{&quot;status&quot;:
			&quot;ok&quot;}</span></span></span></font></font></font></span></span></p></li>
		</ul>
		<li><p style="line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.03in; border: none; padding: 0in">
		<span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><strong><span style="font-variant: normal"><font color="#000000"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">/vision</span></span></span></font></font></font></span></strong></span><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">&nbsp;(POST)</span></span></span></font></font></font></span></p>
		<ul>
			<li><p style="line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.03in; border: none; padding: 0in">
			<strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">Purpose:</span></span></span></font></font></font></span></strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">&nbsp;To
			process input from the&nbsp;</span></span></span></font></font></font></span><span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><span style="font-variant: normal"><font color="#000000"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">vision.py</span></span></span></font></font></font></span></span><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">&nbsp;client,
			which includes fresh visual context.</span></span></span></font></font></font></span></p></li>
			<li><p style="line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.03in; border: none; padding: 0in">
			<strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">Payload:</span></span></span></font></font></font></span></strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">&nbsp;</span></span></span></font></font></font></span><span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><span style="font-variant: normal"><font color="#000000"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">{&quot;text&quot;:
			&quot;user's command&quot;, &quot;vision_context&quot;:
			&quot;description from VLM&quot;}</span></span></span></font></font></font></span></span></p></li>
			<li><p style="line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.03in; border: none; padding: 0in">
			<strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">Returns:</span></span></span></font></font></font></span></strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">&nbsp;</span></span></span></font></font></font></span><span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><span style="font-variant: normal"><font color="#000000"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">{&quot;response&quot;:
			&quot;the final answer from the LLM&quot;}</span></span></span></font></font></font></span></span></p></li>
		</ul>
		<li><p style="line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.03in; border: none; padding: 0in">
		<span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><strong><span style="font-variant: normal"><font color="#000000"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">/audio</span></span></span></font></font></font></span></strong></span><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">&nbsp;(POST)</span></span></span></font></font></font></span></p>
		<ul>
			<li><p style="line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.03in; border: none; padding: 0in">
			<strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">Purpose:</span></span></span></font></font></font></span></strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">&nbsp;To
			process transcribed text from an audio input source.</span></span></span></font></font></font></span></p></li>
			<li><p style="line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.03in; border: none; padding: 0in">
			<strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">Payload:</span></span></span></font></font></font></span></strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">&nbsp;</span></span></span></font></font></font></span><span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><span style="font-variant: normal"><font color="#000000"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">{&quot;text&quot;:
			&quot;transcribed user speech&quot;}</span></span></span></font></font></font></span></span></p></li>
			<li><p style="line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.03in; border: none; padding: 0in">
			<strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">Returns:</span></span></span></font></font></font></span></strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">&nbsp;</span></span></span></font></font></font></span><span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><span style="font-variant: normal"><font color="#000000"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">{&quot;response&quot;:
			&quot;the final answer from the LLM&quot;}</span></span></span></font></font></font></span></span></p></li>
		</ul>
	</ol>
</ul>
<p style="line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.03in; border: none; padding: 0in">
<br/>
<br/>

</p>
<ul>
	<ol start="4">
		<li><p style="line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.03in; border: none; padding: 0in">
		<span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><strong><span style="font-variant: normal"><font color="#000000"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">/update_vision</span></span></span></font></font></font></span></strong></span><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">&nbsp;(POST)</span></span></span></font></font></font></span></p>
		<ul>
			<li><p style="line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.03in; border: none; padding: 0in">
			<strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">Purpose:</span></span></span></font></font></font></span></strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">&nbsp;Allows
			an external service (like&nbsp;</span></span></span></font></font></font></span><span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><span style="font-variant: normal"><font color="#000000"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">vision.py</span></span></span></font></font></font></span></span><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">)
			to update the MCP's visual memory without asking a question.</span></span></span></font></font></font></span></p></li>
			<li><p style="line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.03in; border: none; padding: 0in">
			<strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">Payload:</span></span></span></font></font></font></span></strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">&nbsp;</span></span></span></font></font></font></span><span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><span style="font-variant: normal"><font color="#000000"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">{&quot;vision_context&quot;:
			&quot;new visual description&quot;}</span></span></span></font></font></font></span></span></p></li>
			<li><p style="line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.03in; border: none; padding: 0in">
			<strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">Returns:</span></span></span></font></font></font></span></strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">&nbsp;</span></span></span></font></font></font></span><span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><span style="font-variant: normal"><font color="#000000"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">{&quot;status&quot;:
			&quot;vision context updated&quot;}</span></span></span></font></font></font></span></span></p></li>
		</ul>
	</ol>
</ul>
<p style="line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.19in">
<strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">6.
Code Breakdown</span></span></span></font></font></font></span></strong></p>
<ul>
	<li><p style="line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.03in; border: none; padding: 0in">
	<span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><strong><span style="font-variant: normal"><font color="#000000"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">load_config()</span></span></span></font></font></font></span></strong></span><strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">:</span></span></span></font></font></font></span></strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">&nbsp;Safely
	loads all settings from the&nbsp;</span></span></span></font></font></font></span><span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><span style="font-variant: normal"><font color="#000000"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">.ini</span></span></span></font></font></font></span></span><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">&nbsp;file
	and exits if any critical setting is missing.</span></span></span></font></font></font></span></p></li>
	<li><p style="line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.03in; border: none; padding: 0in">
	<span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><strong><span style="font-variant: normal"><font color="#000000"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">ask_llm()</span></span></span></font></font></font></span></strong></span><strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">:</span></span></span></font></font></font></span></strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">&nbsp;An
	abstraction function that routes the prompt to either the Gemini or
	Ollama API based on the configuration.</span></span></span></font></font></font></span></p></li>
	<li><p style="line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.03in; border: none; padding: 0in">
	<span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><strong><span style="font-variant: normal"><font color="#000000"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">send_to_...()</span></span></span></font></font></font></span></strong></span><strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">&nbsp;functions:</span></span></span></font></font></font></span></strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">&nbsp;A
	set of helper functions (</span></span></span></font></font></font></span><span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><span style="font-variant: normal"><font color="#000000"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">send_to_social_stream</span></span></span></font></font></font></span></span><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">,&nbsp;</span></span></span></font></font></font></span><span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><span style="font-variant: normal"><font color="#000000"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">send_to_tts</span></span></span></font></font></font></span></span><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">)
	that handle the logic of sending the final response to output
	services.</span></span></span></font></font></font></span></p></li>
	<li><p style="line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.03in; border: none; padding: 0in">
	<span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><strong><span style="font-variant: normal"><font color="#000000"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">process_task()</span></span></span></font></font></font></span></strong></span><strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">:</span></span></span></font></font></font></span></strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">&nbsp;</span></span></span></font></font></font></span><strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">This
	is the most important function.</span></span></span></font></font></font></span></strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">&nbsp;It
	contains the core decision-making logic: wake word check, vision
	context handling, and prompt construction.</span></span></span></font></font></font></span></p></li>
	<li><p style="line-height: 0.21in; orphans: 2; widows: 2; margin-bottom: 0.03in; border: none; padding: 0in">
	<strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">Flask&nbsp;</span></span></span></font></font></font></span></strong><span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><strong><span style="font-variant: normal"><font color="#000000"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">@app.route</span></span></span></font></font></font></span></strong></span><strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">&nbsp;functions:</span></span></span></font></font></font></span></strong><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">&nbsp;These
	define the API endpoints and serve as the entry points for all
	external communication, each calling&nbsp;</span></span></span></font></font></font></span><span style="display: inline-block; border-top: 1px solid #1f1f1f; border-bottom: 1px solid #1f1f1f; border-left: none; border-right: none; padding: 0.02in 0in"><span style="font-variant: normal"><font color="#000000"><font face="DM Mono, monospace"><font size="2" style="font-size: 9pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">process_task</span></span></span></font></font></font></span></span><span style="font-variant: normal"><font color="#000000"><font face="Inter, sans-serif"><font size="2" style="font-size: 10pt"><span style="letter-spacing: normal"><span style="font-style: normal"><span style="font-weight: normal">&nbsp;to
	do the heavy lifting.</span></span></span></font></font></font></span></p></li>
</ul>
<p style="line-height: 100%; margin-bottom: 0in"><br/>

</p>
</body>
</html>
