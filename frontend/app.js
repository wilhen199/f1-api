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
      loadResultSprintDriver(driverId, season);
    } else if (tab === "qualifyings") {
      currentSubTabDriver = "Qualifyings";
      loadResultQualifyingDriver(driverId, season);
    } else {
      currentSubTabDriver = "Main Races";
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

function teamAvatar(team) {
  if (team.photo) {
    return `<img class="avatar" src="${team.photo}">`;
  }
  return `<span class="avatar-fallback">${initials(team.name)}</span>`;
}

function teamAvatarProfile(team) {
  if (team.photo) {
    return `<img class="avatar" src="${team.photo}">`;
  }
  return `<span class="avatar-fallback-profile">${initials(team.name)}</span>`;
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
    document.getElementById("content").innerHTML = `<p class="empty-state">${errorData.detail}</p>`;
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
        <td><img class="avatar" src="${row.driver.photo}"> <a href="#/driver/${row.driver.id}?season=${season}">${row.driver.givenName} ${row.driver.familyName}</a></td>
        <td><img class="flagimg" src="${row.driver.flag}"></td>
        <td>
          ${teamAvatar(row.team)}
          <a href="#/team/${row.team.id}?season=${season}">${row.team.name}</a>
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
        ${teamAvatar(row.team)}
        <a href="#/team/${row.team.id}?season=${season}">${row.team.name}</a>
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
      <td><img class="flagimg" src="${row.flag}"></td>
      <td><a href="#/race/${row.round}?season=${season}">${row.raceName}</a></td>
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
      <td><img src="${race.flag}" class="flagimg"> <a href="#/race/${race.round}?season=${season}">${race.raceName}</a></td>
      <td>${teamAvatar(race.team)} <a href="#/team/${race.team.id}?season=${season}">${race.team.name}</a></td>
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
        <a href="${data.driver.info}"><p>🌐 Info</p></a>
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
          <a href="#/driver/${item.driver.id}?season=${season}">${item.driver.givenName} ${item.driver.familyName}</a>
          ${badge(item.position)}
          <span>${item.points} pts</span>
          <span>${item.status}</span>
        </div>`,
        )
        .join("");

      return `
    <tr>
      <td>${race.round}</td>
      <td><img class="flagimg" src="${race.flag}"> <a href="#/race/${race.round}?season=${season}">${race.raceName}</a></td>
      <td>${driversHtml}</td>
    </tr>`;
    })
    .join("");
  content.innerHTML += `
    <div class="profile">
      ${teamAvatarProfile(data.team)}
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
        <a href="${data.team.info}"><p>🌐Info</p></a>
        <span class="back">${backLink()}</span>
      </div>
      <a class="profile-driver" href="#/driver/${data.driver[0].id}?season=${season}">
        <img class="avatar" src="${data.driver[0].photo}">
        <span>${data.driver[0].givenName} ${data.driver[0].familyName}</span>
      </a>
      <a class="profile-driver" href="#/driver/${data.driver[1].id}?season=${season}">
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
          <a href="#/driver/${item.driver.id}?season=${season}">${item.driver.givenName} ${item.driver.familyName}</a>
        </div>
      </td>
      <td>
        <div>
          ${teamAvatar(item.team)}
          <a href="#/team/${item.team.id}?season=${season}">${item.team.name}</a>
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
          <a href="#/driver/${row.driver.id}?season=${season}">${row.driver.givenName} ${row.driver.familyName}</a>
        </div>
      </td>
      <td>
        <div>
          ${teamAvatar(row.team)}
          <a href="#/team/${row.team.id}?season=${season}">${row.team.name}</a>
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
          <img class="avatar" src="${row.driver.photo}">
          <a href="#/driver/${row.driver.id}?season=${season}">${row.driver.givenName} ${row.driver.familyName}</a>
        </div>
      </td>
      <td>
        <div>
          <img class="avatar" src="${row.team.photo}">
          <a href="#/team/${row.team.id}?season=${season}">${row.team.name}</a>
        </div>
      </td>
      <td>${row.Q1 || "-"}</td>
      <td>${row.Q2 || "-"}</td>
      <td>${row.Q3 || "-"}</td>
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
  const content = document.getElementById("content");
  content.innerHTML = "";
  const rowsHTML = data.sprint
    .map(
      (sprint) =>
        `<tr>
      <td>${sprint.round}</td>
      <td><img src="${sprint.flag}" class="flagimg"> <a href="#/race/${sprint.round}?season=${season}">${sprint.raceName}</a></td>
      <td>${teamAvatar(sprint.team)} <a href="#/team/${sprint.team.id}?season=${season}">${sprint.team.name}</a></td>
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
        <h2>${data.driver.givenName} ${data.driver.familyName}  <img class="flagimg" src="${data.driver.flag}"></h2>
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
        <a href="${data.driver.info}"><p>🌐 Info</p></a>
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
  const content = document.getElementById("content");
  content.innerHTML = "";
  const rowsHTML = data.qualifying
    .map(
      (qualifying) =>
        `<tr>
      <td>${qualifying.round}</td>
      <td><img src="${qualifying.flag}" class="flagimg"> <a href="#/race/${qualifying.round}?season=${season}">${qualifying.raceName}</a></td>
      <td>${teamAvatar(qualifying.team)} <a href="#/team/${qualifying.team.id}?season=${season}">${qualifying.team.name}</a></td>
      <td>${badge(qualifying.position)}</td>
      <td>${qualifying.Q1 || "-"}</td>
      <td>${qualifying.Q2 || "-"}</td>
      <td>${qualifying.Q3 || "-"}</td>
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
        <a href="${data.driver.info}"><p>🌐 Info</p></a>
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
            <img class="avatar-tiny" src="${row.pole.driver.photo}">
            <strong>${row.pole.driver.givenName} ${row.pole.driver.familyName}</strong>
            <span>${row.pole.time || "-"}</span>
          </div>`
        : ""
    }
    ${
      row.driver_of_the_day
        ? `<div class="award-chip award-dotd">
            <span class="award-chip-label">DOTD</span>
            <img class="avatar-tiny" src="${row.driver_of_the_day.driver.photo}">
            <strong>${row.driver_of_the_day.driver.givenName} ${row.driver_of_the_day.driver.familyName}</strong>
            <span>${row.driver_of_the_day.percentage}%</span>
          </div>`
        : ""
    }
    ${
      row.fastest_pit_stop
        ? `<div class="award-chip award-pitstop">
            <span class="award-chip-label">FASTEST PIT STOP</span>
            <span class="award-swatch" style="background:#${row.fastest_pit_stop.colour}"></span>
            <strong>${row.fastest_pit_stop.team}</strong>
            <span>${row.fastest_pit_stop.time}</span>
          </div>`
        : ""
    }
    ${
      row.sprint_winner
        ? `<div class="award-chip award-sprint">
            <span class="award-chip-label">SPRINT WIN</span>
            <img class="avatar-tiny" src="${row.sprint_winner.photo}">
            <strong>${row.sprint_winner.givenName} ${row.sprint_winner.familyName}</strong>
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
          <img class="avatar" src="${item.driver.photo}">
          <a href="#/driver/${item.driver.id}?season=${currentAwardsSeason}">${item.driver.givenName} ${item.driver.familyName}</a>
        </div>
      </td>
      <td>
        <div>
          ${teamAvatar(item.team)}
          <a href="#/team/${item.team.id}?season=${currentAwardsSeason}">${item.team.name}</a>
        </div>
      </td>
      <td>${badge(item.grid)}</td>
      <td>${item.points || ""}</td>
    </tr>`,
    )
    .join("");

  card.innerHTML = `
    <div class="gp-card">
      <div class="gp-card-header">
        <span class="gp-round">${row.round}</span>
        <img class="flagimg" src="${row.flag_circuit}">
        <a href="#/race/${row.round}?season=${currentAwardsSeason}"><strong>${row.raceName}</strong></a>
        <span class="gp-card-meta">${row.circuit} · ${row.date}</span>
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
