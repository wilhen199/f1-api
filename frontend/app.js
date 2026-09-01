/* ##### BEGINNING ##### */

document.addEventListener("DOMContentLoaded", async () => {
  console.log("F1 app loaded!");
  await loadSeason();
  window.addEventListener("hashchange", router);
  if (!window.location.hash) {
    window.location.hash = `#/standings/drivers?season=${new Date().getFullYear()}`;
  } else {
    router();
  }

  document.getElementById("navStandings").addEventListener("click", () => {
    const season = document.getElementById("seasonSelect").value;
    window.location.hash = `#/standings/drivers?season=${season}`;
  });
  document.getElementById("navResults").addEventListener("click", () => {
    const season = document.getElementById("seasonSelect").value;
    window.location.hash = `#/results/races?season=${season}`;
  });
  document.getElementById("headerLogo").addEventListener("click", () => {
    /* const season = document.getElementById("seasonSelect").value; */
    window.location.hash = `#/standings/drivers?season=${new Date().getFullYear()}`;
  });

  document.addEventListener("click", async (event) => {
    const link = event.target.closest('a[href^="#/"]');
    if (!link) {
      return;
    }
    event.preventDefault();
    const hash = link.getAttribute("href");
    const { path, params } = parseHash(hash);
    const apiUrl = getApiUrl(path, params);
    if (!apiUrl) {
      window.location.hash = hash;
      return;
    }
    await navigateTo(hash, apiUrl);
  });
});

/* ######################### */
/* #-------- ROUTER -------# */
/* ######################### */

function getRoute() {
  const hash = window.location.hash;
  if (!hash || hash === "#") {
    return {
      path: "/standings/drivers",
      params: new URLSearchParams(),
    };
  }
  const [path, queryString] = hash.substring(1).split("?");
  return {
    path,
    params: new URLSearchParams(queryString || ""),
  };
}

function router() {
  const { path, params } = getRoute();
  const season = params.get("season") || document.getElementById("seasonSelect")?.value || new Date().getFullYear().toString();
  const tab = params.get("tab");

  /*
  # -------------------------
  # STANDINGS
  # -------------------------
   */
  if (path === "/standings/drivers") {
    currentTabStandigs = "Drivers";
    currentDriverId = null;
    currentTeamId = null;
    hideSubTabs();
    document.getElementById("tabsBar").style.display = "flex";
    renderTabsBar("standings");
    setActiveNav("standings");
    loadStandingsDrivers(season);
    setSeasonSelect(season);
    return;
  }

  if (path === "/standings/teams") {
    currentTabStandigs = "Teams";
    currentDriverId = null;
    currentTeamId = null;
    hideSubTabs();
    document.getElementById("tabsBar").style.display = "flex";
    renderTabsBar("standings");
    setActiveNav("standings");
    loadStandingsTeams(season);
    setSeasonSelect(season);
    return;
  }

  /*
  # -------------------------
  # RESULTS - RACES
  # -------------------------
  */

  if (path === "/results/races") {
    currentTabResults = "Races";
    currentDriverId = null;
    currentTeamId = null;
    currentRound = null;
    hideSubTabs();
    document.getElementById("tabsBar").style.display = "flex";
    renderTabsBar("results");
    setActiveNav("results");
    loadRaces(season);
    setSeasonSelect(season);
    return;
  }

  /*
  # -------------------------
  # RESULTS - AWARDS
  # -------------------------
  */

  if (path === "/results/awards") {
    currentTabResults = "Awards";
    currentDriverId = null;
    currentTeamId = null;
    currentRound = null;
    hideSubTabs();
    document.getElementById("tabsBar").style.display = "flex";
    renderTabsBar("results");
    setActiveNav("results");
    loadAwards(season);
    setSeasonSelect(season);
    return;
  }

  /*
  # -------------------------
  # DRIVER
  # -------------------------
  */

  const driverMatch = path.match(/^\/driver\/([^/]+)$/);

  if (driverMatch) {
    const driverId = driverMatch[1];
    currentDriverId = driverId;
    currentTeamId = null;
    currentTabResults = "Drivers";
    document.getElementById("tabsBar").style.display = "flex";
    renderTabsBar("results");
    setActiveNav("results");
    setSeasonSelect(season);
    if (tab === "sprints") {
      currentSubTabDriver = "Sprints";
      renderDriverSubTabs(driverId, season);
      loadResultSprintDriver(driverId, season);
    } else if (tab === "qualifyings") {
      currentSubTabDriver = "Qualifyings";
      renderDriverSubTabs(driverId, season);
      loadResultQualifyingDriver(driverId, season);
    } else {
      currentSubTabDriver = "Main Races";
      renderDriverSubTabs(driverId, season);
      loadResultsDriver(driverId, season);
    }
    return;
  }

  /*
  # -------------------------
  # TEAM
  # -------------------------
  */

  const teamMatch = path.match(/^\/team\/([^/]+)$/);
  if (teamMatch) {
    const teamId = teamMatch[1];
    currentTeamId = teamId;
    currentDriverId = null;
    currentTabResults = "Team";
    hideSubTabs();
    document.getElementById("tabsBar").style.display = "flex";
    renderTabsBar("results");
    setActiveNav("results");
    setSeasonSelect(season);
    loadResultsTeam(teamId, season);
    return;
  }

  /*
  # -------------------------
  # RACE
  # -------------------------
  */

  const raceMatch = path.match(/^\/race\/([^/]+)$/);

  if (raceMatch) {
    const round = raceMatch[1];
    currentRound = round;
    currentDriverId = null;
    currentTeamId = null;
    currentTabResults = "Races";
    document.getElementById("tabsBar").style.display = "flex";
    renderTabsBar("results");
    setActiveNav("results");
    setSeasonSelect(season);
    if (tab === "sprint") {
      currentSubTabRaces = "Sprint";
      renderRaceSubTabs(round, season);
      loadResultSprintRace(round, season);
    } else if (tab === "qualifying") {
      currentSubTabRaces = "Qualifying";
      renderRaceSubTabs(round, season);
      loadResultQualifyingRace(round, season);
    } else {
      currentSubTabRaces = "Main Race";
      renderRaceSubTabs(round, season);
      loadResultMainRace(round, season);
    }
    return;
  }

  /*
  # -------------------------
  # UNKNOWN ROUTE
  # -------------------------
  */
  console.warn("Unknown route:", path);
  window.location.hash = "#/standings/drivers?season=" + season;
}

/* ########################### */
/* #- VARIABLES - UTILITIES -# */
/* ########################### */

let currentTabStandigs = "Drivers";
let currentTabResults = "Races";
let currentDriverId = null;
let currentTeamId = null;
let currentRound = null;
let currentSubTabRaces = "Main Race";
let currentSubTabDriver = "Main Races";

let currentAwardsRows = [];
let currentAwardsSeason = null;

const apiCache = {};

/**
 * Escape HTML characters to prevent XSS attacks
 */
function escapeHtml(text) {
  if (text === null || text === undefined) return "";
  const str = String(text);
  const map = {
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#x27;",
  };

  return str.replace(/[&<>"']/g, (char) => map[char]);
}

function setActiveNav(view) {
  const allNavs = document.querySelectorAll(".nav-link");
  for (const nav of allNavs) {
    nav.classList.remove("active");
  }
  const navId = view === "standings" ? "navStandings" : "navResults";
  document.getElementById(navId).classList.add("active");
}

function setSeasonSelect(season) {
  const select = document.getElementById("seasonSelect");
  if (select && select.value !== String(season)) {
    select.value = String(season);
  }
}

function hideSubTabs() {
  const subTabBar = document.getElementById("subTabsBar");
  if (subTabBar) {
    subTabBar.classList.add("hidden");
    subTabBar.classList.remove("active");
  }
}

function badge(position) {
  const pos = Number(position);
  if (isNaN(pos) || pos <= 0) {
    return '<span class="badge">${escapeHtml(position)}</span>';
  }
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
  if (!name) return "";
  const words = String(name).split(" ");
  let result = "";
  for (const word of words) {
    result += word[0];
  }
  return result;
}

function driverAvatar(driver, givenName, familyName) {
  const driverName = (givenName || "") + " " + (familyName || "");
  if (driver.photo) {
    return `<img class="avatar" src="${escapeHtml(driver.photo)}">`;
  }
  return `<span class="avatar-fallback">${escapeHtml(initials(driverName))}</span>`;
}

function driverAvatarProfile(driver, givenName, familyName) {
  const driverName = (givenName || "") + " " + (familyName || "");
  if (driver.photo) {
    return `<img class="avatar" src="${escapeHtml(driver.photo)}">`;
  }
  return `<span class="avatar-fallback-profile">${escapeHtml(initials(driverName))}</span>`;
}

function teamAvatar(team) {
  if (team.photo) {
    return `<img class="avatar" src="${escapeHtml(team.photo)}">`;
  }
  return `<span class="avatar-fallback">${escapeHtml(initials(team.name))}</span>`;
}

function teamAvatarProfile(team) {
  if (team.photo) {
    return `<img class="avatar" src="${escapeHtml(team.photo)}">`;
  }
  return `<span class="avatar-fallback-profile">${escapeHtml(initials(team.name))}</span>`;
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
  if (apiCache[url]) {
    return apiCache[url];
  }

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
    document.getElementById("content").innerHTML = `<p class="empty-state">${escapeHtml(errorData.detail)}</p>`;
    return null;
  }

  const data = await response.json();
  apiCache[url] = data;
  return data;
}

function parseHash(hash) {
  const [path, queryString] = hash.substring(1).split("?");
  return { path, params: new URLSearchParams(queryString || "") };
}

function getApiUrl(path, params) {
  const season = params.get("season");

  if (!season) {
    return null;
  }

  if (path === "/standings/drivers") {
    return `/api/standings/drivers?season=${season}`;
  }

  if (path === "/standings/teams") {
    return `/api/standings/teams?season=${season}`;
  }

  if (path === "/results/races") {
    return `/api/results?season=${season}`;
  }

  if (path === "/results/awards") {
    return `/api/awards?season=${season}`;
  }

  const driverMatch = path.match(/^\/driver\/([^/]+)$/);

  if (driverMatch) {
    return `/api/driver/${driverMatch[1]}?season=${season}`;
  }

  const teamMatch = path.match(/^\/team\/([^/]+)$/);

  if (teamMatch) {
    return `/api/team/${teamMatch[1]}?season=${season}`;
  }

  const raceMatch = path.match(/^\/race\/([^/]+)$/);

  if (raceMatch) {
    return `/api/results/race/${raceMatch[1]}?season=${season}`;
  }

  return null;
}

async function navigateTo(hash, apiUrl) {
  const data = await fetchApi(apiUrl);

  if (!data) {
    return;
  }

  window.location.hash = hash;
}

function backLink() {
  return '<a class="back" href="#" onclick="history.back(); return false;">◀️ Back</a>';
}

/* ######################### */
/* #----- MENU - TABS -----# */
/* ######################### */

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
        if (i === "Drivers") {
          window.location.hash = `#/standings/drivers?season=${season}`;
        } else {
          window.location.hash = `#/standings/teams?season=${season}`;
        }
      } else {
        if (i === "Races") {
          window.location.hash = `#/results/races?season=${season}`;
        } else {
          window.location.hash = `#/results/awards?season=${season}`;
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
      let hash;
      if (subTabName === "Main Race") {
        hash = `#/race/${round}?season=${season}`;
      } else if (subTabName === "Sprint") {
        hash = `#/race/${round}?season=${season}&tab=sprint`;
      } else {
        hash = `#/race/${round}?season=${season}&tab=qualifying`;
      }
      window.location.hash = hash;
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
      let hash;
      if (subTabName === "Main Races") {
        hash = `#/driver/${driverId}?season=${season}`;
      } else if (subTabName === "Sprints") {
        hash = `#/driver/${driverId}?season=${season}&tab=sprints`;
      } else {
        hash = `#/driver/${driverId}?season=${season}&tab=qualifyings`;
      }
      window.location.hash = hash;
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
    changeSeason(select.value);
  });
}

function changeSeason(season) {
  const { path, params } = getRoute();
  params.set("season", season);
  window.location.hash = `${path}?${params.toString()}`;
}

/* ######################### */
/* #------ STANDINGS ------# */
/* ######################### */

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
        <td>${driverAvatar(row.driver, row.driver.givenName, row.driver.familyName)} <a href="#/driver/${escapeHtml(row.driver.id)}?season=${season}">${escapeHtml(row.driver.givenName)} ${escapeHtml(row.driver.familyName)}</a></td>
        <td><img class="flagimg" src="${escapeHtml(row.driver.flag)}"></td>
        <td>
          ${teamAvatar(row.team)}
          <a href="#/team/${escapeHtml(row.team.id)}?season=${season}">${escapeHtml(row.team.name)}</a>
        </td>
        <td>${escapeHtml(row.points)}</td>
        <td>${escapeHtml(row.wins)}</td>
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
  if (data.message) {
    document.getElementById("content").innerHTML = `<p class="empty-state">${escapeHtml(data.message)}</p>`;
    return;
  }

  const content = document.getElementById("content");
  content.innerHTML = "";
  const rowsHTML = data.rows
    .map(
      (row) => `
    <tr>
      <td>${badge(row.position)}</td>
      <td>
        ${teamAvatar(row.team)}
        <a href="#/team/${escapeHtml(row.team.id)}?season=${season}">${escapeHtml(row.team.name)}</a>
    </td>
      <td><img class="flagimg" src="${escapeHtml(row.team.flag)}"></td>
      <td>${escapeHtml(row.points)}</td>
      <td>${escapeHtml(row.wins)}</td>
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

/* ####################### */
/* #------ RESULTS ------# */
/* ####################### */

async function loadRaces(season) {
  const data = await fetchApi(`/api/results?season=${season}`);
  if (!data) return;
  const content = document.getElementById("content");
  content.innerHTML = "";
  const rowsHTML = data.rows
    .map(
      (row) => `
    <tr>
      <td><img class="flagimg" src="${escapeHtml(row.flag)}"></td>
      <td><a href="#/race/${escapeHtml(row.round)}?season=${season}">${escapeHtml(row.raceName)}</a></td>
      <td>${escapeHtml(row.circuit)}</td>
      <td>${escapeHtml(row.date)}</td>
      <td>${escapeHtml(row.laps)}</td>
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
      <td>${escapeHtml(race.round)}</td>
      <td><img src="${escapeHtml(race.flag)}" class="flagimg"> <a href="#/race/${escapeHtml(race.round)}?season=${season}">${escapeHtml(race.raceName)}</a></td>
      <td>${teamAvatar(race.team)} <a href="#/team/${escapeHtml(race.team.id)}?season=${season}">${escapeHtml(race.team.name)}</a></td>
      <td>${badge(race.grid)}</td>
      <td>${badge(race.position)}</td>
      <td>${escapeHtml(race.points)}</td>
      <td>${escapeHtml(race.status)}</td>
    </tr>`,
    )
    .join("");
  content.innerHTML += `
    <div class="profile">
      ${driverAvatarProfile(data.driver, data.driver.givenName, data.driver.familyName)}
      <div class="profile-info">
        <h2>${escapeHtml(data.driver.givenName)} ${escapeHtml(data.driver.familyName)}  <img class="flagimg" src="${escapeHtml(data.driver.flag)}"> </h2>
        <div class="profile-stats">
          <div>
            <span class="stat-num">${badge(data.position)}</span>
            <span class="stat-label">POS</span>
          </div>
          <div>
            <span class="stat-num">${escapeHtml(data.points)}</span>
            <span class="stat-label">PTS</span>
          </div>
          <div>
            <span class="stat-num">${escapeHtml(data.wins)}</span>
            <span class="stat-label">WINS</span>
          </div>
        </div>
        <a href="${escapeHtml(data.driver.info)}"><p>🌐 Info</p></a>
        <span class="back">${backLink()}</span>
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
          <a href="#/driver/${escapeHtml(item.driver.id)}?season=${season}">${escapeHtml(item.driver.givenName)} ${escapeHtml(item.driver.familyName)}</a>
          ${badge(item.position)}
          <span>${escapeHtml(item.points)} pts</span>
          <span>${escapeHtml(item.status)}</span>
        </div>`,
        )
        .join("");

      return `
    <tr>
      <td>${escapeHtml(race.round)}</td>
      <td><img class="flagimg" src="${escapeHtml(race.flag)}"> <a href="#/race/${escapeHtml(race.round)}?season=${season}">${escapeHtml(race.raceName)}</a></td>
      <td>${driversHtml}</td>
    </tr>`;
    })
    .join("");
  content.innerHTML += `
    <div class="profile">
      ${teamAvatarProfile(data.team)}
      <div class="profile-info">
        <h2>${escapeHtml(data.team.name)} <img class="flagimg" src="${escapeHtml(data.team.flag)}"></h2>
        <div class="profile-stats">
          <div>
            <span class="stat-num">${badge(data.position)}</span>
            <span class="stat-label">POS</span>
          </div>
          <div>
            <span class="stat-num">${escapeHtml(data.points)}</span>
            <span class="stat-label">PTS</span>
          </div>
          <div>
            <span class="stat-num">${escapeHtml(data.wins)}</span>
            <span class="stat-label">WINS</span>
          </div>
        </div>
        <a href="${escapeHtml(data.team.info)}"><p>🌐Info</p></a>
        <span class="back">${backLink()}</span>
      </div>
      <a class="profile-driver" href="#/driver/${escapeHtml(data.driver[0].id)}?season=${season}">
        ${driverAvatarProfile(data.driver[0], data.driver[0].givenName, data.driver[0].familyName)}
        <span>${escapeHtml(data.driver[0].givenName)} ${escapeHtml(data.driver[0].familyName)}</span>
      </a>
      <a class="profile-driver" href="#/driver/${escapeHtml(data.driver[1].id)}?season=${season}">
        ${driverAvatarProfile(data.driver[1], data.driver[1].givenName, data.driver[1].familyName)}
        <span>${escapeHtml(data.driver[1].givenName)} ${escapeHtml(data.driver[1].familyName)}</span>
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
          ${driverAvatar(item.driver, item.driver.givenName, item.driver.familyName)}
          <a href="#/driver/${escapeHtml(item.driver.id)}?season=${season}">${escapeHtml(item.driver.givenName)} ${escapeHtml(item.driver.familyName)}</a>
        </div>
      </td>
      <td>
        <div>
          ${teamAvatar(item.team)}
          <a href="#/team/${escapeHtml(item.team.id)}?season=${season}">${escapeHtml(item.team.name)}</a>
        </div>
      </td>
      <td>${badge(item.grid)}</td>
      <td>${escapeHtml(item.laps)}</td>
      <td>${escapeHtml(item.time || "-")}</td>
      <td>${escapeHtml(item.fastestLap || "-")}</td>
      <td>${escapeHtml(item.points)}</td>
      <td>${escapeHtml(item.status)}</td>
    </tr>`,
    )
    .join("");
  content.innerHTML += `
    <div class="race-header">
      <span class="gp-round">${escapeHtml(round)}</span>
      <img class="flagimg" src="${escapeHtml(data.race.flag)}">
      <h2>${escapeHtml(data.race.raceName)}</h2>
      <div>${escapeHtml(data.race.circuit)}   -   ${escapeHtml(data.race.date)}</div>
    </div>
    <span class="back">${backLink()}</span>
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
    content.innerHTML = `<p class="empty-state">No sprint race found for ${escapeHtml(data.race.raceName)} (${season}).</p>`;
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
          ${driverAvatar(row.driver, row.driver.givenName, row.driver.familyName)}
          <a href="#/driver/${escapeHtml(row.driver.id)}?season=${season}">${escapeHtml(row.driver.givenName)} ${escapeHtml(row.driver.familyName)}</a>
        </div>
      </td>
      <td>
        <div>
          ${teamAvatar(row.team)}
          <a href="#/team/${escapeHtml(row.team.id)}?season=${season}">${escapeHtml(row.team.name)}</a>
        </div>
      </td>
      <td>${badge(row.grid)}</td>
      <td>${escapeHtml(row.laps)}</td>
      <td>${escapeHtml(row.time || "-")}</td>
      <td>${escapeHtml(row.fastestLap || "-")}</td>
      <td>${escapeHtml(row.points)}</td>
      <td>${escapeHtml(row.status)}</td>
    </tr>
  `,
    )
    .join("");
  content.innerHTML += `
  <div class="race-header">
    <span class="gp-round">${escapeHtml(round)}</span>
    <img class="flagimg" src="${escapeHtml(data.race.flag)}">
    <h2>${escapeHtml(data.race.raceName)}</h2>
    <div>${escapeHtml(data.race.circuit)}   -   ${escapeHtml(data.race.date)}</div>
  </div>
  <span class="back">${backLink()}</span>
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
          ${driverAvatar(row.driver, row.driver.givenName, row.driver.familyName)}
          <a href="#/driver/${escapeHtml(row.driver.id)}?season=${season}">${escapeHtml(row.driver.givenName)} ${escapeHtml(row.driver.familyName)}</a>
        </div>
      </td>
      <td>
        <div>
          ${teamAvatar(row.team)}
          <a href="#/team/${escapeHtml(row.team.id)}?season=${season}">${escapeHtml(row.team.name)}</a>
        </div>
      </td>
      <td>${escapeHtml(row.Q1 || "-")}</td>
      <td>${escapeHtml(row.Q2 || "-")}</td>
      <td>${escapeHtml(row.Q3 || "-")}</td>
    </tr>
  `,
    )
    .join("");
  content.innerHTML += `
  <div class="race-header">
    <span class="gp-round">${escapeHtml(round)}</span>
    <img class="flagimg" src="${escapeHtml(data.race.flag)}">
    <h2>${escapeHtml(data.race.raceName)}</h2>
    <div>${escapeHtml(data.race.circuit)}   -   ${escapeHtml(data.race.date)}</div>
  </div>
  <span class="back">${backLink()}</span>
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
  if (!data.sprint) {
    document.getElementById("content").innerHTML = `<p class="empty-state">The Sprint Race did not take place until 2021</p>`;
    return;
  }
  const content = document.getElementById("content");
  content.innerHTML = "";
  const rowsHTML = data.sprint
    .map(
      (sprint) =>
        `<tr>
      <td>${escapeHtml(sprint.round)}</td>
      <td><img src="${escapeHtml(sprint.flag)}" class="flagimg"> <a href="#/race/${escapeHtml(sprint.round)}?season=${season}">${escapeHtml(sprint.raceName)}</a></td>
      <td>${teamAvatar(sprint.team)} <a href="#/team/${escapeHtml(sprint.team.id)}?season=${season}">${escapeHtml(sprint.team.name)}</a></td>
      <td>${badge(sprint.grid)}</td>
      <td>${badge(sprint.position)}</td>
      <td>${escapeHtml(sprint.points)}</td>
      <td>${escapeHtml(sprint.status)}</td>
    </tr>`,
    )
    .join("");
  content.innerHTML += `
    <div class="profile">
      ${driverAvatarProfile(data.driver, data.driver.givenName, data.driver.familyName)}
      <div class="profile-info">
        <h2>${escapeHtml(data.driver.givenName)} ${escapeHtml(data.driver.familyName)}  <img class="flagimg" src="${escapeHtml(data.driver.flag)}"></h2>
        <div class="profile-stats">
          <div>
            <span class="stat-num">${badge(data.position)}</span>
            <span class="stat-label">POS</span>
          </div>
          <div>
            <span class="stat-num">${escapeHtml(data.points)}</span>
            <span class="stat-label">PTS</span>
          </div>
          <div>
            <span class="stat-num">${escapeHtml(data.wins)}</span>
            <span class="stat-label">WINS</span>
          </div>
        </div>
        <a href="${escapeHtml(data.driver.info)}"><p>🌐 Info</p></a>
        <span class="back">${backLink()}</span>
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
  if (!data.qualifying) {
    document.getElementById("content").innerHTML = `<p class="empty-state">There is no qualifying data from source</p>`;
    return;
  }
  const content = document.getElementById("content");
  content.innerHTML = "";
  const rowsHTML = data.qualifying
    .map(
      (qualifying) =>
        `<tr>
      <td>${escapeHtml(qualifying.round)}</td>
      <td><img src="${escapeHtml(qualifying.flag)}" class="flagimg"> <a href="#/race/${escapeHtml(qualifying.round)}?season=${season}">${escapeHtml(qualifying.raceName)}</a></td>
      <td>${teamAvatar(qualifying.team)} <a href="#/team/${escapeHtml(qualifying.team.id)}?season=${season}">${escapeHtml(qualifying.team.name)}</a></td>
      <td>${badge(qualifying.position)}</td>
      <td>${escapeHtml(qualifying.Q1 || "-")}</td>
      <td>${escapeHtml(qualifying.Q2 || "-")}</td>
      <td>${escapeHtml(qualifying.Q3 || "-")}</td>
    </tr>`,
    )
    .join("");
  content.innerHTML += `
    <div class="profile">
      ${driverAvatarProfile(data.driver, data.driver.givenName, data.driver.familyName)}
      <div class="profile-info">
        <h2>${escapeHtml(data.driver.givenName)} ${escapeHtml(data.driver.familyName)}  <img class="flagimg" src="${escapeHtml(data.driver.flag)}"> </h2>
        <div class="profile-stats">
          <div>
            <span class="stat-num">${badge(data.position)}</span>
            <span class="stat-label">POS</span>
          </div>
          <div>
            <span class="stat-num">${escapeHtml(data.points)}</span>
            <span class="stat-label">PTS</span>
          </div>
          <div>
            <span class="stat-num">${escapeHtml(data.wins)}</span>
            <span class="stat-label">WINS</span>
          </div>
        </div>
        <a href="${escapeHtml(data.driver.info)}"><p>🌐 Info</p></a>
        <span class="back">${backLink()}</span>
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

/* ####################### */
/* #------ AWARDS ------# */
/* ####################### */

async function loadAwards(season) {
  const data = await fetchApi(`/api/awards?season=${season}`);
  if (!data) return;
  currentAwardsRows = data.rows;
  currentAwardsSeason = season;
  const content = document.getElementById("content");
  content.innerHTML = `
    <h2 class="view-title">${season} Per-GP Highlights</h2>
    <div class="awards-controls"><select id="awardsRoundSelect"></select></div>
    <span class="back">${backLink()}</span>
    <div id="awardsCard"></div>
  `;
  const select = document.getElementById("awardsRoundSelect");
  for (const row of data.rows) {
    const option = document.createElement("option");
    option.value = row.round;
    option.textContent = `R${row.round} - ${row.raceName}`;
    select.appendChild(option);
  }
  select.addEventListener("change", () => {
    renderAwardsCard(select.value);
  });
  renderAwardsCard(data.rows[0].round);
  hideSubTabs();
}

function renderAwardsCard(round) {
  const row = currentAwardsRows.find((r) => String(r.round) === String(round));
  const card = document.getElementById("awardsCard");
  if (!row) {
    card.innerHTML = `<p class="empty-state">No data for this round.</p>`;
    return;
  }

  const badgesHtml = `
    ${
      row.pole
        ? `<div class="award-chip award-pole">
            <span class="award-chip-label">POLE</span>
            <img class="avatar-tiny" src="${escapeHtml(row.pole.driver.photo)}">
            <strong>${escapeHtml(row.pole.driver.givenName)} ${escapeHtml(row.pole.driver.familyName)}</strong>
            <span>${escapeHtml(row.pole.time || "-")}</span>
          </div>`
        : ""
    }
    ${
      row.driver_of_the_day
        ? `<div class="award-chip award-dotd">
            <span class="award-chip-label">DOTD</span>
            <img class="avatar-tiny" src="${escapeHtml(row.driver_of_the_day.driver.photo)}">
            <strong>${escapeHtml(row.driver_of_the_day.driver.givenName)} ${escapeHtml(row.driver_of_the_day.driver.familyName)}</strong>
            <span>${escapeHtml(row.driver_of_the_day.percentage)}%</span>
          </div>`
        : ""
    }
    ${
      row.fastest_pit_stop
        ? `<div class="award-chip award-pitstop">
            <span class="award-chip-label">FASTEST PIT STOP</span>
            <span class="award-swatch" style="background:#${escapeHtml(row.fastest_pit_stop.colour)}"></span>
            <strong>${escapeHtml(row.fastest_pit_stop.team)}</strong>
            <span>${escapeHtml(row.fastest_pit_stop.time)}</span>
          </div>`
        : ""
    }
    ${
      row.sprint_winner
        ? `<div class="award-chip award-sprint">
            <span class="award-chip-label">SPRINT WIN</span>
            <img class="avatar-tiny" src="${escapeHtml(row.sprint_winner.photo)}">
            <strong>${escapeHtml(row.sprint_winner.givenName)} ${escapeHtml(row.sprint_winner.familyName)}</strong>
          </div>`
        : ""
    }
  `;

  const top5Html = row.top_5
    .map(
      (item, index) => `
    <tr>
      <td>${badge(index + 1)}</td>
      <td>
        <div>
          <img class="avatar" src="${escapeHtml(item.driver.photo)}">
          <a href="#/driver/${escapeHtml(item.driver.id)}?season=${currentAwardsSeason}">${escapeHtml(item.driver.givenName)} ${escapeHtml(item.driver.familyName)}</a>
        </div>
      </td>
      <td>
        <div>
          ${teamAvatar(item.team)}
          <a href="#/team/${escapeHtml(item.team.id)}?season=${currentAwardsSeason}">${escapeHtml(item.team.name)}</a>
        </div>
      </td>
      <td>${badge(item.grid)}</td>
      <td>${escapeHtml(item.points || "")}</td>
    </tr>`,
    )
    .join("");

  card.innerHTML = `
    <div class="gp-card">
      <div class="gp-card-header">
        <span class="gp-round">${escapeHtml(row.round)}</span>
        <img class="flagimg" src="${escapeHtml(row.flag_circuit)}">
        <a href="#/race/${escapeHtml(row.round)}?season=${currentAwardsSeason}"><strong>${escapeHtml(row.raceName)}</strong></a>
        <span class="gp-card-meta">${escapeHtml(row.circuit)} · ${escapeHtml(row.date)}</span>
      </div>
      <div class="award-badges">${badgesHtml}</div>
      <h3>TOP 5</h3>
      <div class="tablewrap">
        <table>
          <thead>
            <tr>
              <th>POS</th>
              <th>DRIVER</th>
              <th>TEAM</th>
              <th>GRID</th>
              <th>PTS</th>
            </tr>
          </thead>
          <tbody>${top5Html}</tbody>
        </table>
      </div>
    </div>`;
}
