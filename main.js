// Minimal bootstrap to load the existing pygame-web build without changing game logic
// Keeps desktop Python game in main.py; this file is for web hosts that expect a JS entry.

(function () {
	function navigateToIndex() {
		if (typeof window === "undefined") return;
		var target = "./index.html";
		if (!location.pathname.endsWith("/index.html")) {
			location.replace(target);
		}
	}

	// If loaded in an HTML page that is not index.html, redirect to the web build
	if (document.readyState === "loading") {
		document.addEventListener("DOMContentLoaded", navigateToIndex);
	} else {
		navigateToIndex();
	}
})();

// Optional: export a start function for environments that import this file
// without executing it directly.
export function startWebGame() {
	if (typeof window !== "undefined") {
		window.location.replace("./index.html");
	}
}


