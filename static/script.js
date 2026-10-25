
document.addEventListener("DOMContentLoaded", function () {
    const forms = document.querySelectorAll("form");
    let scannerForm = null;

    // Find the main scanner form
    forms.forEach(function (form) {
        if (
            form.querySelector('select[name="scan_type"]') &&
            form.querySelector('[name="text"]')
        ) {
            scannerForm = form;
        }
    });

    if (scannerForm) {
        const input = scannerForm.querySelector('[name="text"]');
        const scanButton = scannerForm.querySelector(
            'button[type="submit"], input[type="submit"]'
        );

        // Create a message area
        const message = document.createElement("p");
        message.className = "js-message";
        message.setAttribute("role", "status");
        message.setAttribute("aria-live", "polite");
        input.insertAdjacentElement("afterend", message);

        scannerForm.addEventListener("submit", function (event) {
            if (!input.value.trim()) {
                event.preventDefault();
                message.textContent =
                    "Please enter a URL or message before scanning.";
                input.focus();
                return;
            }

            message.textContent = "Analyzing your input...";

            if (scanButton) {
                scanButton.disabled = true;
                scanButton.classList.add("is-scanning");

                if (scanButton.tagName === "INPUT") {
                    scanButton.value = "Scanning...";
                } else {
                    scanButton.textContent = "Scanning...";
                }
            }
        });

        input.addEventListener("input", function () {
            message.textContent = "";

            if (scanButton) {
                scanButton.disabled = false;
                scanButton.classList.remove("is-scanning");

                if (scanButton.tagName === "INPUT") {
                    scanButton.value = "Analyze";
                } else {
                    scanButton.textContent = "Analyze";
                }
            }
        });
    }

    // Improve the scan result experience
    const result = document.querySelector(".scan-result");

    if (result) {
        result.setAttribute("tabindex", "-1");

        setTimeout(function () {
            result.scrollIntoView({
                behavior: "smooth",
                block: "center"
            });
        }, 150);

        // Add a copy-result button
        const copyButton = document.createElement("button");
        copyButton.type = "button";
        copyButton.className = "copy-result-btn";
        copyButton.textContent = "Copy Scan Result";

        result.appendChild(copyButton);

        copyButton.addEventListener("click", async function () {
            const originalText = result.innerText
                .replace("Copy Scan Result", "")
                .replace("Copied!", "")
                .trim();

            try {
                await navigator.clipboard.writeText(originalText);
                copyButton.textContent = "Copied!";
            } catch (error) {
                copyButton.textContent =
                    "Copy unavailable — select the result text manually.";
            }

            setTimeout(function () {
                copyButton.textContent = "Copy Scan Result";
            }, 2000);
        });
    }
});
