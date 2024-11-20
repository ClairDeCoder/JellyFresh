/////////////////////////////////////////////////////////////////////
// Get library configs if exist, load default forms, remove libraries
/////////////////////////////////////////////////////////////////////
let libraryCount = 0;

function addLibrary(libraryData = null) {
    const libraryContainer = document.getElementById("libraries");
    const libraryDiv = document.createElement("div");
    libraryDiv.className = "library";
    libraryDiv.id = `library-${libraryCount + 1}`;

    const mediaType = libraryData?.media_type || "movies";
    const timePeriod = libraryData?.time_period || "1_week";
    const newReleasesFolder = libraryData?.new_releases_folder || "";

    libraryDiv.innerHTML = `
        <div class="library-header">
            <h3>Library ${libraryCount + 1}</h3>
            <button type="button" class="remove-library" onclick="removeLibrary(${libraryCount + 1})">X</button>
        </div>
        <label for="media_type-${libraryCount + 1}">Select Media Type:</label>
        <select id="media_type-${libraryCount + 1}" name="media_type-${libraryCount + 1}" required>
            <option value="movies" ${mediaType === "movies" ? "selected" : ""}>Movies</option>
            <option value="shows" ${mediaType === "shows" ? "selected" : ""}>TV Shows</option>
            <option value="both" ${mediaType === "both" ? "selected" : ""}>Both</option>
        </select>
        
        <label for="period-${libraryCount + 1}">Select Time Period:</label>
        <select id="period-${libraryCount + 1}" name="period-${libraryCount + 1}" required>
            <option value="1_week" ${timePeriod === "1_week" ? "selected" : ""}>Last Week</option>
            <option value="2_weeks" ${timePeriod === "2_weeks" ? "selected" : ""}>Last 2 Weeks</option>
            <option value="1_month" ${timePeriod === "1_month" ? "selected" : ""}>Last Month</option>
            <option value="2_months" ${timePeriod === "2_months" ? "selected" : ""}>Last 2 Months</option>
            <option value="6_months" ${timePeriod === "6_months" ? "selected" : ""}>Last 6 Months</option>
            <option value="1_year" ${timePeriod === "1_year" ? "selected" : ""}>Last Year</option>
        </select>

        <label for="new_releases_folder-${libraryCount + 1}">New Releases Folder:</label>
        <input type="text" id="new_releases_folder-${libraryCount + 1}" name="new_releases_folder-${libraryCount + 1}" placeholder="/path/to/new/releases" value="${newReleasesFolder}" required>
    `;

    libraryContainer.appendChild(libraryDiv);
    libraryCount++;
    document.getElementById("library_count").value = libraryCount;
}

function removeLibrary(index) {
    const libraryDiv = document.getElementById(`library-${index}`);
    if (libraryDiv) {
        libraryDiv.remove();
        libraryCount--;
        document.getElementById("library_count").value = libraryCount;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const libraryContainer = document.getElementById("libraries");

    // Get libraries from the backend
    fetch('/libraries')
        .then(response => response.json())
        .then(libraries => {

            if (libraries && libraries.length > 0) {
                libraryCount = 0;
                libraryContainer.innerHTML = "";
                // Populate the form with existing libraries
                libraries.forEach(library => {
                    addLibrary({
                        media_type: library.media_type,
                        time_period: getPeriodKey(library.time_period),
                        new_releases_folder: library.new_releases_folder
                    });
                });
            } else {
                // If no libraries exist, reset libraryCount and add a single blank form
                libraryContainer.innerHTML = "";
                libraryCount = 0; // Reset library count
                addLibrary();
            }
        })
        .catch(err => {
            console.error("Error loading libraries:", err);
            // Reset libraryCount and add a single blank form as a fallback
            libraryContainer.innerHTML = "";
            libraryCount = 0; // Reset library count
            addLibrary();
        });
});

// Helper function to map time_period to dropdown keys
function getPeriodKey(timePeriod) {
    const periods = {
        604800: "1_week",
        1209600: "2_weeks",
        2592000: "1_month",
        5184000: "2_months",
        15724800: "6_months",
        31536000: "1_year"
    };
    return periods[timePeriod] || "1_week"; // Default to "1_week" if no match
}

/////////////////////////////////////////////////////////////////////
// Show results after scan/Retrieve latest logs
///////////////////////////////////////////////////////////////////// 
document.addEventListener("DOMContentLoaded", () => {
    const logsButton = document.getElementById("toggle-logs-button");
    const logsSection = document.getElementById("logs");
    const logContent = document.getElementById("log-content");

    // Toggle visibility of logs and fetch new logs on each click
    logsButton.addEventListener("click", () => {
        logsSection.classList.toggle("open");

        if (logsSection.classList.contains("open")) {
            logsSection.style.display = "block";

            // Fetch the latest logs whenever the section is opened
            fetch("/logs/recent")
                .then((response) => {
                    if (!response.ok) {
                        throw new Error("Failed to fetch logs.");
                    }
                    return response.text();
                })
                .then((data) => {
                    logContent.textContent = data;
                })
                .catch((error) => {
                    console.error("Error fetching logs:", error);
                    logContent.textContent = "Unable to load logs.";
                });
        } else {
            logsSection.style.display = "none";
        }
    });
});


/////////////////////////////////////////////////////////////////////
// Scheduler setup - get current schedule config && set new config
/////////////////////////////////////////////////////////////////////            
document.addEventListener('DOMContentLoaded', () => {
    const modeToggle = document.getElementById("mode-toggle");
    const modeLabel = document.getElementById("mode-label");
    const automaticOptions = document.getElementById("automatic-options");
    const form = document.querySelector("#settings-section form");
    const nextScanInfo = document.getElementById("next-scan-info");

    // Get existing scheduler settings from the backend
    fetch('/scheduler')
        .then(response => response.json())
        .then(scheduler => {

            // Apply settings from the configuration
            const mode = scheduler.mode || "manual"; // Default to "manual"
            modeToggle.checked = mode === "automatic";
            modeLabel.textContent = modeToggle.checked ? "Automatic" : "Manual";
            automaticOptions.style.display = modeToggle.checked ? "block" : "none";

            // Set frequency and time if available
            if (scheduler.frequency) {
                document.getElementById("frequency").value = scheduler.frequency;
            }
            if (scheduler.time) {
                document.getElementById("time").value = scheduler.time;
            }

            // Display the next scan info if available
            if (scheduler.next_scan) {
                const formattedNextScan = new Date(scheduler.next_scan).toLocaleString();
                nextScanInfo.textContent = `Next scan: ${formattedNextScan}`;
            }
        })
        .catch(err => {
            console.error("Error loading scheduler settings:", err);
        });

    // Update label and options visibility on toggle change
    modeToggle.addEventListener("change", () => {
        const isAutomatic = modeToggle.checked;
        modeLabel.textContent = isAutomatic ? "Automatic" : "Manual";
        automaticOptions.style.display = isAutomatic ? "block" : "none";
    });

    // Handle form submission to save scheduler settings
    form.addEventListener("submit", event => {
        event.preventDefault();

        const formData = new FormData(form);
        formData.set("mode", modeToggle.checked ? "automatic" : "manual");

        fetch('/scheduler', {
            method: "POST",
            body: formData,
        })
            .then(response => response.json())
            .then(data => {
                if (data.next_scan) {
                    const formattedTime = new Date(data.next_scan).toLocaleString();
                    nextScanInfo.textContent = `Next scan scheduled for: ${formattedTime}`;
                } else if (data.error) {
                    nextScanInfo.textContent = `Error: ${data.error}`;
                } else {
                    nextScanInfo.textContent = "Settings updated successfully.";
                }
                // Automatically hide the success/error message after 5 seconds
                setTimeout(() => {
                    nextScanInfo.textContent = "";
                }, 5000);
            })
            .catch(err => {
                console.error("Error saving scheduler settings:", err);
                nextScanInfo.textContent = "An unexpected error occurred.";
                setTimeout(() => {
                    nextScanInfo.textContent = "";
                }, 5000);
            });
    });
});

/////////////////////////////////////////////////////////////////////
// Save libraries to config file and scan accordingly
/////////////////////////////////////////////////////////////////////
function submitForm(event) {
    event.preventDefault();

    // Clear previous errors and results
    const errorMessageElement = document.getElementById("error-message");
    const resultsElement = document.getElementById("results");
    const resultsMoviesElement = document.getElementById("results-movies");
    const resultsShowsElement = document.getElementById("results-shows");
    const spinnerElement = document.getElementById("spinner");

    if (errorMessageElement) {
        errorMessageElement.textContent = "";
        errorMessageElement.style.display = "none";
    }

    if (resultsElement) {
        resultsElement.style.display = "none";
    }

    if (resultsMoviesElement) {
        resultsMoviesElement.innerHTML = "";
    }

    if (resultsShowsElement) {
        resultsShowsElement.innerHTML = "";
    }

    if (spinnerElement) {
        spinnerElement.style.display = "block";
    }

    // Gather form data
    const formData = new FormData(event.target);

    // Send POST request to /new_releases
    fetch("/new_releases", {
        method: "POST",
        body: formData,
    })
        .then(response => response.json())
        .then(data => {
            if (spinnerElement) {
                spinnerElement.style.display = "none";
            }

            if (data.error && errorMessageElement) {
                errorMessageElement.textContent = data.error;
                errorMessageElement.style.display = "block";
                return;
            }

            if (data.results) {
                // Process movies
                if (data.results.movies && data.results.movies.length > 0) {
                    data.results.movies.forEach(movie => {
                        const li = document.createElement("li");
                        li.textContent = movie;
                        resultsMoviesElement.appendChild(li);
                    });
                } else {
                    const li = document.createElement("li");
                    li.textContent = "No movies linked.";
                    resultsMoviesElement.appendChild(li);
                }

                // Process shows
                if (data.results.shows && data.results.shows.length > 0) {
                    data.results.shows.forEach(show => {
                        const li = document.createElement("li");
                        li.textContent = show;
                        resultsShowsElement.appendChild(li);
                    });
                } else {
                    const li = document.createElement("li");
                    li.textContent = "No shows linked.";
                    resultsShowsElement.appendChild(li);
                }

                // Show the results box
                if (resultsElement) {
                    resultsElement.style.display = "block";
                }
            }
        })
        .catch(error => {
            console.error("Error:", error);
            if (spinnerElement) {
                spinnerElement.style.display = "none";
            }
            if (errorMessageElement) {
                errorMessageElement.textContent = "An unexpected error occurred.";
                errorMessageElement.style.display = "block";
            }
        });
}
window.onload = function() {
    addLibrary();
};