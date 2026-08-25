/* ##### BEGINNING ##### */

document.addEventListener("DOMContentLoaded", () => {
  console.log("F1 app loaded!");
  loadSeason();
  renderTabsBar("standings");
  document.getElementById("navStandings").classList.add("active");

  document.getElementById("navStandings").addEventListener("click", () => {
    hideSubTabs();
    document.getElementById("tabsBar").style.display = "flex";
    renderTabsBar("standings");
    const allNavs = document.querySelectorAll(".nav-link");
    for (const n of allNavs) {
      n.classList.remove("active");
    }
    document.getElementById("navStandings").classList.add("active");
    const season = document.getElementById("seasonSelect").value;
    if (currentTabStandigs === "Drivers") {
      loadStandingsDrivers(season);
    } else {
      loadStandingsTeams(season);
    }
  });

  document.getElementById("navResults").addEventListener("click", () => {
    hideSubTabs();
    document.getElementById("tabsBar").style.display = "flex";
    currentTabResults = "Races";
    renderTabsBar("results");
    const allNavs = document.querySelectorAll(".nav-link");
    for (const n of allNavs) {
      n.classList.remove("active");
    }
    document.getElementById("navResults").classList.add("active");
    const season = document.getElementById("seasonSelect").value;
    loadRaces(season);
  });

  document.getElementById("headerLogo").addEventListener("click", () => {
    document.getElementById("navStandings").click();
  });
});

/* ##### VARIABLES AND UTILITIES ##### */
let currentTabStandigs = "Drivers";
let currentTabResults = "Races";
let currentDriverId = null;
let currentTeamId = null;
let currentRound = null;
let currentSubTabRaces = "Main Race";
let currentSubTabDriver = "Main Races";

function hideSubTabs() {
  const subTabBar = document.getElementById("subTabsBar");
  if (subTabBar) {
    subTabBar.classList.add("hidden");
    subTabBar.classList.remove("active");
  }
}

function badge(position) {
  const pos = Number(position);
  if (pos === 1) {
    return '<span class="badge pos-1">1</span>';
  } else if (pos === 2) {
    return '<span class="badge pos-2">2</span>';
  } else if (pos === 3) {
    return '<span class="badge pos-3">3</span>';
  }
  return `<span class="badge">${pos}</span>`;
}

function initials(name) {
  const words = name.split(" ");
  let result = "";
  for (const word of words) {
    result += word[0];
  }
  return result;
}

function showToast(message) {
  const toast = document.getElementById("toast");
  toast.textContent = message;
  toast.classList.remove("hidden");

  setTimeout(() => {
    toast.classList.add("hidden");
  }, 5000);
}

function handleRateLimit(response) {
  const retryAfter = response.headers.get("Retry-After") || "60";
  showToast(`Too many requests. Please wait ${retryAfter} seconds and try again.`);
}

async function fetchApi(url) {
  const response = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
    },
  });
  if (response.status === 429) {
    handleRateLimit(response);
    return null;
  }

  if (!response.ok) {
    const errorData = await response.json();
    document.getElementById("content").innerHTML = `<p class="empty-state">${errorData.detail}</p>`;
    return null;
  }

  return await response.json();
}

function goToDriver(driverId, season) {
  currentDriverId = driverId;
  document.getElementById("tabsBar").style.display = "flex";
  renderTabsBar("results");

  const allNavs = document.querySelectorAll(".nav-link");
  for (const n of allNavs) {
    n.classList.remove("active");
  }
  document.getElementById("navResults").classList.add("active");

  loadResultsDriver(driverId, season);
}

function goToTeam(teamId, season) {
  hideSubTabs();
  currentTeamId = teamId;
  document.getElementById("tabsBar").style.display = "flex";
  renderTabsBar("results");

  const allNavs = document.querySelectorAll(".nav-link");
  for (const n of allNavs) {
    n.classList.remove("active");
  }
  document.getElementById("navResults").classList.add("active");

  loadResultsTeam(teamId, season);
}

function goToRace(round, season) {
  currentSubTabRaces = "Main Race";
  hideSubTabs();
  currentRound = round;
  document.getElementById("tabsBar").style.display = "flex";
  renderTabsBar("results");
  const allNavs = document.querySelectorAll(".nav-link");
  for (const n of allNavs) {
    n.classList.remove("active");
  }
  document.getElementById("navResults").classList.add("active");
  renderRaceSubTabs(round, season);
  loadResultMainRace(round, season);
}

/* ##### MENU - TABS ##### */

async function renderTabsBar(view = "standings") {
  const tabBar = document.getElementById("tabsBar");
  tabBar.innerHTML = "";
  let tabToDisplay = [];
  if (view === "standings") {
    tabToDisplay = ["Drivers", "Teams"];
  } else if (view === "results") {
    tabToDisplay = ["Races", "Awards"];
  }

  for (const i of tabToDisplay) {
    const tab = document.createElement("div");
    tab.textContent = i;
    tab.className = "tab";

    if ((view === "standings" && i === currentTabStandigs) || (view === "results" && i === currentTabResults)) {
      tab.classList.add("active");
    }

    tab.addEventListener("click", () => {
      const allTabs = document.querySelectorAll(".tab");
      for (const t of allTabs) {
        t.classList.remove("active");
      }
      tab.classList.add("active");

      const season = document.getElementById("seasonSelect").value;

      if (view === "standings") {
        currentTabStandigs = i;
        if (i === "Driver") {
          loadStandingsDrivers(season);
        } else {
          loadStandingsTeams(season);
        }
      } else if (view === "results") {
        currentTabResults = i;
        if (i === "Races") {
          loadRaces(season);
        } else {
          loadAwards(season);
        }
      }
    });
    tabBar.appendChild(tab);
  }
}

async function renderRaceSubTabs(round, season) {
  const subTabBar = document.getElementById("subTabsBar");
  subTabBar.classList.remove("hidden");
  subTabBar.classList.add("active");
  subTabBar.innerHTML = "";
  const subTabToDisplay = ["Main Race", "Sprint", "Qualifying"];
  for (const subTabName of subTabToDisplay) {
    const subTab = document.createElement("div");
    subTab.textContent = subTabName;
    subTab.className = "subtab";
    if (subTabName === currentSubTabRaces) {
      subTab.classList.add("active");
    }
    subTab.addEventListener("click", () => {
      const allSubTabs = document.querySelectorAll(".subtab");
      for (const st of allSubTabs) {
        st.classList.remove("active");
      }
      subTab.classList.add("active");
      currentSubTabRaces = subTabName;

      if (subTabName === "Main Race") {
        loadResultMainRace(round, season);
      } else if (subTabName === "Sprint") {
        loadResultSprintRace(round, season);
      } else {
        loadResultQualifyingRace(round, season);
      }
    });
    subTabBar.appendChild(subTab);
  }
}

async function renderDriverSubTabs(driverId, season) {
  const subTabBar = document.getElementById("subTabsBar");

  subTabBar.classList.remove("hidden");
  subTabBar.classList.add("active");
  subTabBar.innerHTML = "";

  const subTabToDisplay = ["Main Races", "Sprints", "Qualifyings"];

  for (const subTabName of subTabToDisplay) {
    const subTab = document.createElement("div");
    subTab.textContent = subTabName;
    subTab.className = "subtab";

    if (subTabName === currentSubTabDriver) {
      subTab.classList.add("active");
    }

    subTab.addEventListener("click", () => {
      const allSubTabs = document.querySelectorAll(".subtab");
      for (const st of allSubTabs) {
        st.classList.remove("active");
      }
      subTab.classList.add("active");

      if (subTabName === "Main Races") {
        loadResultsDriver(driverId, season);
      } else if (subTabName === "Sprints") {
        loadResultSprintDriver(driverId, season);
      } else {
        loadResultQualifyingDriver(driverId, season);
      }
    });
    subTabBar.appendChild(subTab);
  }
}

async function loadSeason() {
  const seasons = await fetchApi("/api/seasons");
  if (!seasons) return;

  const select = document.getElementById("seasonSelect");
  select.innerHTML = "";

  for (const season of seasons) {
    const option = document.createElement("option");
    option.value = season;
    option.textContent = season;
    select.appendChild(option);
  }
  select.addEventListener("change", () => {
    const currentView = document.querySelector(".nav-link.active").id.replace("nav", "").toLowerCase();
    if (currentView === "standings") {
      hideSubTabs();
      const currentTab = document.querySelector("#tabsBar .tab.active").textContent;
      if (currentTab === "Drivers") {
        loadStandingsDrivers(select.value);
      } else {
        loadStandingsTeams(select.value);
      }
    } else if (currentView === "results") {
      if (currentTabResults === "Races") {
        hideSubTabs();
        loadRaces(select.value);
      } else if (currentTabResults === "Drivers") {
        loadResultsDriver(currentDriverId, select.value);
      } else if (currentTabResults === "Team") {
        hideSubTabs();
        loadResultsTeam(currentTeamId, select.value);
      } else if (currentTabResults === "RaceDetail") {
        loadResultMainRace(currentRound, select.value);
      } else {
        hideSubTabs();
        loadAwards(select.value);
      }
    }
  });

  loadStandingsDrivers(select.value);
}

/* ##### STANDIGS ##### */

async function loadStandingsDrivers(season) {
  const data = await fetchApi(`/api/standings/drivers?season=${season}`);
  if (!data) return;
  const content = document.getElementById("content");
  content.innerHTML = "";
  const rowsHTML = data.rows
    .map(
      (row) => `
      <tr>
        <td>${badge(row.position)}</td>
        <td><img class="avatar" src="${row.driver.photo}"> <a href="#" onclick="goToDriver('${row.driver.id}', '${season}')">${row.driver.givenName} ${row.driver.familyName}</a></td>
        <td><img class="flagimg" src="${row.driver.flag}"></td>
        <td>
          ${row.team.photo ? `<img class="avatar" src="${row.team.photo}">` : `<span class="avatar-fallback">${initials(row.team.name)}</span>`}
          <a href="#" onclick="goToTeam('${row.team.id}', '${season}')">${row.team.name}</a>
        </td>
        <td>${row.points}</td>
        <td>${row.wins}</td>
    </tr>`,
    )
    .join("");

  content.innerHTML += `
    <h2 class="view-title"> ${season} Driver Standing</h2>
    <div class="tablewrap">
    <table>
      <thead>
        <tr>
          <th>POS</th>
          <th>DRIVER</th>
          <th>NAT</th>
          <th>TEAM</th>
          <th>PTS</th>
          <th>WINS</th>
        </tr>
      </thead>
      <tbody>
        ${rowsHTML}
      </tbody>
    </table>
    </div>`;
}

async function loadStandingsTeams(season) {
  const data = await fetchApi(`/api/standings/teams?season=${season}`);
  if (!data) return;
  const content = document.getElementById("content");
  content.innerHTML = "";
  const rowsHTML = data.rows
    .map(
      (row) => `
    <tr>
      <td>${badge(row.position)}</td>
      <td>
        ${row.team.photo ? `<img class="avatar" src="${row.team.photo}">` : `<span class="avatar-fallback">${initials(row.team.name)}</span>`}
        <a href="#" onclick="goToTeam('${row.team.id}', '${season}')">${row.team.name}</a>
    </td>
      <td><img class="flagimg" src="${row.team.flag}"></td>
      <td>${row.points}</td>
      <td>${row.wins}</td>
    </tr>`,
    )
    .join("");

  content.innerHTML += `
    <h2 class="view-title"> ${season} Team Standing</h2>
    <div class="tablewrap">
    <table>
      <thead>
        <tr>
          <th>POS</th>
          <th>TEAM</th>
          <th>NAT</th>
          <th>PTS</th>
          <th>WINS</th>
        </tr>
      </thead>
      <tbody>
        ${rowsHTML}
      </tbody>
    </table>
    </div>`;
}

/* ##### RESULTS ##### */

async function loadRaces(season) {
  const data = await fetchApi(`/api/results?season=${season}`);
  if (!data) return;
  const content = document.getElementById("content");
  content.innerHTML = "";
  const rowsHTML = data.rows
    .map(
      (row) => `
    <tr>
      <td><img class="flagimg" src="${row.flag}"></td>
      <td><a href="#" onclick="goToRace('${row.round}', '${season}')">${row.raceName}</a></td>
      <td>${row.circuit}</td>
      <td>${row.date}</td>
      <td>${row.laps}</td>
    </tr>`,
    )
    .join("");
  content.innerHTML += `
    <h2 class="view-title"> ${season} Races List</h2>
    <div class="tablewrap">
    <table>
      <thead>
        <tr>
          <th></th>
          <th>GRAND PRIX</th>
          <th>CIRCUIT</th>
          <th>DATE</th>
          <th>LAPS</th>
        </tr>
      </thead>
      <tbody>
        ${rowsHTML}
      </tbody>
    </table>
    </div>`;
}

async function loadResultsDriver(driverId, season) {
  const data = await fetchApi(`/api/driver/${driverId}?season=${season}`);
  if (!data) return;
  const content = document.getElementById("content");
  content.innerHTML = "";
  const rowsHTML = data.races
    .map(
      (race) =>
        `<tr>
      <td>${race.round}</td>
      <td><img src="${race.flag}" class="flagimg"> <a href="#" onclick="goToRace('${race.round}', '${season}')">${race.raceName}</a></td>
      <td><img src="${race.team.photo}" class="avatar"> <a href="#" onclick="goToTeam('${race.team.id}', '${season}')">${race.team.name}</a></td>
      <td>${badge(race.grid)}</td>
      <td>${badge(race.position)}</td>
      <td>${race.points}</td>
      <td>${race.status}</td>
    </tr>`,
    )
    .join("");
  content.innerHTML += `
    <div class="profile">
      <img class="avatar" src="${data.driver.photo}">
      <div class="profile-info">
        <h2>${data.driver.givenName} ${data.driver.familyName}  <img class="flagimg" src="${data.driver.flag}"> </h2>
        <div class="profile-stats">
          <div>
          <span class="stat-num">${badge(data.position)}</span>
          <span class="stat-label">POS</span>
          </div>
          <div>

          <span class="stat-num">${data.points}</span>
          <span class="stat-label">PTS</span>
          </div>
          <div>
          <span class="stat-num">${data.wins}</span>
          <span class="stat-label">WINS</span>
          </div>
        </div>
        <a href="${data.driver.info}"><p>Info 🌐</p></a>
      </div>
    </div>
    <h3> ${season} SEASON RESULTS</h3>
    <div class="tablewrap">
    <table>
      <thead>
        <tr>
          <th>ROUND</th>
          <th>GRAND PRIX</th>
          <th>TEAM</th>
          <th>GRID</th>
          <th>RESULT</th>
          <th>PTS</th>
          <th>STATUS</th>
        </tr>
      </thead>
      <tbody>
        ${rowsHTML}
      </tbody>
    </table>
    </div>`;
  renderDriverSubTabs(driverId, season);
}

async function loadResultsTeam(teamId, season) {
  const data = await fetchApi(`/api/team/${teamId}?season=${season}`);
  if (!data) return;
  const content = document.getElementById("content");
  content.innerHTML = "";

  const rowsHTML = data.races
    .map((race) => {
      const driversHtml = race.drivers
        .map(
          (item) =>
            `
        <div class="driver-row">
          <a href="#" onclick="goToDriver('${item.driver.id}', '${season}')">${item.driver.givenName} ${item.driver.familyName}</a>
          ${badge(item.position)}
          <span>${item.points} pts</span>
          <span>${item.status}</span>
        </div>`,
        )
        .join("");

      return `
    <tr>
      <td>${race.round}</td>
      <td><img class="flagimg" src="${race.flag}"> <a href="#" onclick="goToRace('${race.round}', '${season}')">${race.raceName}</a></td>
      <td>${driversHtml}</td>
    </tr>`;
    })
    .join("");
  content.innerHTML += `
  <div class="profile">
    <img class="avatar" src="${data.team.photo}">
    <div class="profile-info">
      <h2>${data.team.name} <img class="flagimg" src="${data.team.flag}"></h2>
      <div class="profile-stats">
        <div>
          <span class="stat-num">${badge(data.position)}</span>
          <span class="stat-label">POS</span>
        </div>
        <div>
          <span class="stat-num">${data.points}</span>
          <span class="stat-label">PTS</span>
        </div>
        <div>
          <span class="stat-num">${data.wins}</span>
          <span class="stat-label">WINS</span>
        </div>
      </div>
      <a href="${data.team.info}"><p>Info 🌐</p></a>
    </div>
    <a class="profile-driver" href="#" onclick="goToDriver('${data.driver[0].id}', '${season}')">
      <img class="avatar" src="${data.driver[0].photo}">
      <span>${data.driver[0].givenName} ${data.driver[0].familyName}</span>
    </a>
    <a class="profile-driver" href="#" onclick="goToDriver('${data.driver[1].id}', '${season}')">
      <img class="avatar" src="${data.driver[1].photo}">
      <span>${data.driver[1].givenName} ${data.driver[1].familyName}</span>
    </a>
  </div>
  <h3> ${season} GP RESULTS</h3>
    <div class="tablewrap">
    <table>
      <thead>
        <tr>
          <th>ROUND</th>
          <th>GRAND PRIX</th>
          <th>DRIVERS</th>
        </tr>
      </thead>
      <tbody>
        ${rowsHTML}
      </tbody>
    </table>
    </div>`;
}

async function loadResultMainRace(round, season) {
  const data = await fetchApi(`/api/results/race/${round}?season=${season}`);
  if (!data) return;
  const content = document.getElementById("content");
  content.innerHTML = "";
  const rowsHTML = data.results
    .map(
      (item) => `
    <tr>
      <td><span class="badge">${badge(item.position)}</span></td>
      <td>
        <div>
          <img class="avatar" src="${item.driver.photo}">
          <a href="#" onclick="goToDriver('${item.driver.id}', '${season}')">${item.driver.givenName} ${item.driver.familyName}</a>
        </div>
      </td>
      <td>
        <div>
          <img class="avatar" src="${item.team.photo}">
          <a href="#" onclick="goToTeam('${item.team.id}', '${season}')">${item.team.name}</a>
        </div>
      </td>
      <td>${badge(item.grid)}</td>
      <td>${item.laps}</td>
      <td>${item.time}</td>
      <td>${item.fastestLap}</td>
      <td>${item.points}</td>
      <td>${item.status}</td>
    </tr>`,
    )
    .join("");
  content.innerHTML += `
  <div class="race-header">
    <span class="gp-round">${round}</span>
    <img class="flagimg" src="${data.race.flag}">
    <h2>${data.race.raceName}</h2>
    <div>${data.race.circuit}   -   ${data.race.date}</div>
  </div>
  <div class="tablewrap">
    <table>
      <thead>
        <tr>
          <th>POS</th>
          <th>DRIVER</th>
          <th>TEAM</th>
          <th>GRID</th>
          <th>LAPS</th>
          <th>TIME</th>
          <th>FASTEST LAP</th>
          <th>PTS</th>
          <th>STATUS</th>
        </tr>
      </thead>
      <tbody>
        ${rowsHTML}
      </tbody>
    </table>
    </div>`;
}

async function loadResultSprintRace(round, season) {
  const data = await fetchApi(`/api/results/race/${round}?season=${season}`);
  if (!data) return;
  const content = document.getElementById("content");
  if (!data.has_sprint) {
    content.innerHTML = `<p class="empty-state">No sprint race found for ${data.race.raceName} (${season}).</p>`;
    return;
  }
  content.innerHTML = "";
  const rowsHTML = data.sprint
    .map(
      (row) => `
    <tr>
      <td><span class="badge">${badge(row.position)}</span></td>
      <td>
        <div>
          <img class="avatar" src="${row.driver.photo}">
          <a href="#" onclick="goToDriver('${row.driver.id}', '${season}')">${row.driver.givenName} ${row.driver.familyName}</a>
        </div>
      </td>
      <td>
        <div>
          <img class="avatar" src="${row.team.photo}">
          <a href="#" onclick="goToTeam('${row.team.id}', '${season}')">${row.team.name}</a>
        </div>
      </td>
      <td>${badge(row.grid)}</td>
      <td>${row.laps}</td>
      <td>${row.time}</td>
      <td>${row.fastestLap}</td>
      <td>${row.points}</td>
      <td>${row.status}</td>
    </tr>
  `,
    )
    .join("");
  content.innerHTML += `
  <div class="race-header">
    <span class="gp-round">${round}</span>
    <img class="flagimg" src="${data.race.flag}">
    <h2>${data.race.raceName}</h2>
    <div>${data.race.circuit}   -   ${data.race.date}</div>
  </div>
  <div class="tablewrap">
    <table>
      <thead>
        <tr>
          <th>POS</th>
          <th>DRIVER</th>
          <th>TEAM</th>
          <th>GRID</th>
          <th>LAPS</th>
          <th>TIME</th>
          <th>FASTEST LAP</th>
          <th>PTS</th>
          <th>STATUS</th>
        </tr>
      </thead>
      <tbody>
        ${rowsHTML}
      </tbody>
    </table>
    </div>`;
}

async function loadResultQualifyingRace(round, season) {
  const data = await fetchApi(`/api/results/race/${round}?season=${season}`);
  if (!data) return;
  const content = document.getElementById("content");
  content.innerHTML = "";
  const rowsHTML = data.qualifying
    .map(
      (row) => `
    <tr>
      <td><span class="badge">${badge(row.position)}</span></td>
      <td>
        <div>
          <img class="avatar" src="${row.driver.photo}">
          <a href="#" onclick="goToDriver('${row.driver.id}', '${season}')">${row.driver.givenName} ${row.driver.familyName}</a>
        </div>
      </td>
      <td>
        <div>
          <img class="avatar" src="${row.team.photo}">
          <a href="#" onclick="goToTeam('${row.team.id}', '${season}')">${row.team.name}</a>
        </div>
      </td>
      <td>${row.q1 || "-"}</td>
      <td>${row.q2 || "-"}</td>
      <td>${row.q3 || "-"}</td>
    </tr>
  `,
    )
    .join("");
  content.innerHTML += `
  <div class="race-header">
    <span class="gp-round">${round}</span>
    <img class="flagimg" src="${data.race.flag}">
    <h2>${data.race.raceName}</h2>
    <div>${data.race.circuit}   -   ${data.race.date}</div>
  </div>
  <div class="tablewrap">
    <table>
      <thead>
        <tr>
          <th>POS</th>
          <th>DRIVER</th>
          <th>TEAM</th>
          <th>Q1</th>
          <th>Q2</th>
          <th>Q3</th>
        </tr>
      </thead>
      <tbody>
        ${rowsHTML}
      </tbody>
    </table>
    </div>`;
}

async function loadResultSprintDriver(driverId, season) {
  const data = await fetchApi(`/api/driver/${driverId}?season=${season}`);
  if (!data) return;
  const content = document.getElementById("content");
  content.innerHTML = "";
  const rowsHTML = data.sprint
    .map(
      (sprint) =>
        `<tr>
      <td>${sprint.round}</td>
      <td><img src="${sprint.flag}" class="flagimg"> <a href="#" onclick="goToRace('${sprint.round}', '${season}')">${sprint.raceName}</a></td>
      <td><img src="${sprint.team.photo}" class="avatar"> <a href="#" onclick="goToTeam('${sprint.team.id}', '${season}')">${sprint.team.name}</a></td>
      <td>${badge(sprint.grid)}</td>
      <td>${badge(sprint.position)}</td>
      <td>${sprint.points}</td>
      <td>${sprint.status}</td>
    </tr>`,
    )
    .join("");
  content.innerHTML += `
    <div class="profile">
      <img class="avatar" src="${data.driver.photo}">
      <div class="profile-info">
        <h2>${data.driver.givenName} ${data.driver.familyName}  <img class="flagimg" src="${data.driver.flag}"> </h2>
        <div class="profile-stats">
          <div>
          <span class="stat-num">${badge(data.position)}</span>
          <span class="stat-label">POS</span>
          </div>
          <div>

          <span class="stat-num">${data.points}</span>
          <span class="stat-label">PTS</span>
          </div>
          <div>
          <span class="stat-num">${data.wins}</span>
          <span class="stat-label">WINS</span>
          </div>
        </div>
        <a href="${data.driver.info}"><p>Info 🌐</p></a>
      </div>
    </div>
    <h3> ${season} SPRINT RESULTS</h3>
    <div class="tablewrap">
    <table>
      <thead>
        <tr>
          <th>ROUND</th>
          <th>GRAND PRIX</th>
          <th>TEAM</th>
          <th>GRID</th>
          <th>RESULT</th>
          <th>PTS</th>
          <th>STATUS</th>
        </tr>
      </thead>
      <tbody>
        ${rowsHTML}
      </tbody>
    </table>
    </div>`;
}

async function loadResultQualifyingDriver(driverId, season) {
  const data = await fetchApi(`/api/driver/${driverId}?season=${season}`);
  if (!data) return;
  const content = document.getElementById("content");
  content.innerHTML = "";
  const rowsHTML = data.qualifying
    .map(
      (qualifying) =>
        `<tr>
      <td>${qualifying.round}</td>
      <td><img src="${qualifying.flag}" class="flagimg"> <a href="#" onclick="goToRace('${qualifying.round}', '${season}')">${qualifying.raceName}</a></td>
      <td><img src="${qualifying.team.photo}" class="avatar"> <a href="#" onclick="goToTeam('${qualifying.team.id}', '${season}')">${qualifying.team.name}</a></td>
      <td>${badge(qualifying.position)}</td>
      <td>${qualifying.Q1}</td>
      <td>${qualifying.Q2}</td>
      <td>${qualifying.Q3}</td>
    </tr>`,
    )
    .join("");
  content.innerHTML += `
    <div class="profile">
      <img class="avatar" src="${data.driver.photo}">
      <div class="profile-info">
        <h2>${data.driver.givenName} ${data.driver.familyName}  <img class="flagimg" src="${data.driver.flag}"> </h2>
        <div class="profile-stats">
          <div>
          <span class="stat-num">${badge(data.position)}</span>
          <span class="stat-label">POS</span>
          </div>
          <div>

          <span class="stat-num">${data.points}</span>
          <span class="stat-label">PTS</span>
          </div>
          <div>
          <span class="stat-num">${data.wins}</span>
          <span class="stat-label">WINS</span>
          </div>
        </div>
        <a href="${data.driver.info}"><p>Info 🌐</p></a>
      </div>
    </div>
    <h3> ${season} QUALIFYING RESULTS</h3>
    <div class="tablewrap">
    <table>
      <thead>
        <tr>
          <th>ROUND</th>
          <th>GRAND PRIX</th>
          <th>TEAM</th>
          <th>POS</th>
          <th>Q1</th>
          <th>Q2</th>
          <th>Q3</th>
        </tr>
      </thead>
      <tbody>
        ${rowsHTML}
      </tbody>
    </table>
    </div>`;
}

async function loadAwards(season) {
  const data = await fetchApi(`/api/awards?season=${season}`);
  if (!data) return;
  const content = document.getElementById("content");
  let rowsHTML = "";
  content.innerHTML = "";
  for (const race of data) {
    const round = race.round;
    const raceName = race.raceName;
    const circuit = race.Circuit.circuitName;
    const date = race.date;
    const laps = race.laps;
    const country = race.Circuit.Location.country;

    rowsHTML += `
    <tr>
      <td>${country}</td>
      <td><a href="/race/${round}?season=${season}">${raceName}</a></td>
      <td>${circuit}</td>
      <td>${date}</td>
      <td>${laps}</td>
    </tr>`;
  }
  content.innerHTML += `
    <h2 class="view-title"> ${season} Awards</h2>
    <div class="tablewrap">
    <table>
      <thead>
        <tr>
          <th></th>
          <th>GRAND PRIX</th>
          <th>CIRCUIT</th>
          <th>DATE</th>
          <th>LAPS</th>
        </tr>
      </thead>
      <tbody>
        ${rowsHTML}
      </tbody>
    </table>
    </div>`;
}
