import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import fs from 'node:fs/promises';

const require = createRequire(import.meta.url);
const playwrightModule = process.env.PORTFOLIO_PLAYWRIGHT_MODULE ?? 'playwright';
const { chromium } = require(playwrightModule);

const repositoryRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const outputDirectory = path.join(repositoryRoot, 'assets', 'images', 'industrial-portfolio');
const urls = {
  plc: process.env.PORTFOLIO_PLC_URL ?? 'http://localhost:5088',
  gateway: process.env.PORTFOLIO_GATEWAY_UI_URL ?? 'http://localhost:5279',
  twinForge: process.env.PORTFOLIO_TWINFORGE_URL ?? 'http://localhost:18081',
  oee: process.env.PORTFOLIO_OEE_URL ?? 'http://localhost:18083',
  oeeApi: process.env.PORTFOLIO_OEE_API_URL ?? 'http://localhost:18082',
};
const oeeUsername = process.env.PORTFOLIO_OEE_USER ?? 'admin';
const oeePassword = process.env.PORTFOLIO_OEE_PASSWORD;

if (!oeePassword) {
  throw new Error('PORTFOLIO_OEE_PASSWORD is required for local OEEAnalyzer capture.');
}

await fs.mkdir(outputDirectory, { recursive: true });

const browser = await chromium.launch({
  headless: true,
  executablePath: process.env.PORTFOLIO_CHROMIUM_PATH,
});
const context = await browser.newContext({
  viewport: { width: 1920, height: 1080 },
  deviceScaleFactor: 1,
  locale: 'ko-KR',
  timezoneId: 'Asia/Seoul',
  colorScheme: 'dark',
});

const captured = [];

function toLocalInput(date) {
  const local = new Date(date.getTime() - date.getTimezoneOffset() * 60_000);
  return local.toISOString().slice(0, 19);
}

async function savePage(page, fileName, options = {}) {
  const target = path.join(outputDirectory, fileName);
  await page.screenshot({ path: target, animations: 'disabled', ...options });
  captured.push(target);
}

async function saveLocator(locator, fileName) {
  const target = path.join(outputDirectory, fileName);
  await locator.screenshot({ path: target, animations: 'disabled' });
  captured.push(target);
}

async function waitForExternalOee(timeoutMs = 30_000) {
  const deadline = Date.now() + timeoutMs;
  let latest = null;

  while (Date.now() < deadline) {
    const response = await fetch(`${urls.twinForge}/api/integrations/oee/synchronize`, { method: 'POST' });
    if (!response.ok) throw new Error(`TwinForge OEE synchronization failed: HTTP ${response.status}`);
    latest = await response.json();
    if (latest.connected && latest.performance != null && latest.quality != null && latest.oee != null) return latest;
    await new Promise((resolve) => setTimeout(resolve, 2_000));
  }

  throw new Error(`External OEE did not become complete before capture: ${JSON.stringify(latest)}`);
}

try {
  const plc = await context.newPage();
  await plc.goto(urls.plc, { waitUntil: 'networkidle' });
  await plc.getByRole('button', { name: 'Tag Monitor' }).click();
  await plc.getByRole('heading', { name: 'Simulation and Tag Monitor' }).waitFor();
  await plc.getByText('Speed_PV', { exact: true }).first().waitFor();
  await savePage(plc, 'plc-04-live-tags.png');

  const gateway = await context.newPage();
  await gateway.goto(urls.gateway, { waitUntil: 'networkidle' });
  await gateway.getByText('DockerModbus', { exact: true }).click();
  await gateway.getByText('PlcSimulation', { exact: true }).click();
  await gateway.getByRole('heading', { name: 'PlcSimulation / Tags' }).waitFor();
  const closeAssistant = gateway.locator('#chatbot-panel.open button[title="Close"]');
  if (await closeAssistant.count()) await closeAssistant.click({ force: true });
  await gateway.getByText('Total Items:').waitFor();
  await savePage(gateway, 'gateway-03-tags.png');

  await fetch(`${urls.twinForge}/api/mes/reset`, { method: 'POST' });
  await fetch(`${urls.twinForge}/api/mes/start`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ scenario: 'Automotive' }),
  });
  await waitForExternalOee();

  const twin = await context.newPage();
  await twin.goto(urls.twinForge, { waitUntil: 'networkidle' });
  await twin.getByRole('button', { name: '운영 대시보드' }).click();
  await twin.getByRole('heading', { name: 'MES Simulation' }).waitFor();
  await twin.getByText(/^twinforge-MO-/).waitFor({ timeout: 30_000 });
  const mesPanel = twin.getByRole('heading', { name: 'MES Simulation' }).locator('xpath=ancestor::section[1]');
  const externalOeePanel = twin.getByRole('heading', { name: 'External OEEAnalyzer' }).locator('xpath=ancestor::section[1]');
  await saveLocator(mesPanel, 'twin-01-mes-dashboard.png');
  await saveLocator(externalOeePanel, 'oee-03-production-context.png');

  await twin.getByRole('button', { name: '가상 공장' }).click();
  await twin.getByRole('heading', { name: '자동차 제조 디지털트윈' }).waitFor();
  await savePage(twin, 'twin-04-3d-factory.png');
  await fs.copyFile(
    path.join(outputDirectory, 'twin-04-3d-factory.png'),
    path.join(outputDirectory, 'twin-04-3d.png'),
  );
  captured.push(path.join(outputDirectory, 'twin-04-3d.png'));

  const oee = await context.newPage();
  await new Promise((resolve) => setTimeout(resolve, 8_000));
  const loginResponse = await fetch(`${urls.oeeApi}/api/auth/login`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ username: oeeUsername, password: oeePassword }),
  });
  if (!loginResponse.ok) throw new Error(`OEEAnalyzer login failed: HTTP ${loginResponse.status}`);
  const login = await loginResponse.json();
  await oee.goto(urls.oee, { waitUntil: 'networkidle' });
  await oee.evaluate(({ token, role, username }) => {
    sessionStorage.setItem('token', token);
    sessionStorage.setItem('role', role);
    sessionStorage.setItem('username', username);
  }, { token: login.token, role: login.role, username: oeeUsername });

  await oee.goto(`${urls.oee}/admin/integration`, { waitUntil: 'networkidle' });
  await oee.getByRole('heading', { name: '4-System OEE Control Room' }).waitFor();
  await oee.getByRole('heading', { name: 'OEE Window Ledger' }).waitFor();
  await oee.getByLabel('To', { exact: true }).fill(toLocalInput(new Date(Date.now() - 8_000)));
  await oee.getByRole('button', { name: 'Refresh Analysis' }).click();
  await oee.locator('tbody tr').first().waitFor({ timeout: 30_000 });
  await savePage(oee, 'oee-01-integration-overview.png');
  const oeeLedger = oee.getByRole('heading', { name: 'OEE Window Ledger' }).locator('xpath=ancestor::section[1]');
  await saveLocator(oeeLedger, 'oee-02-live-oee.png');

  await oee.goto(`${urls.oee}/admin/config`, { waitUntil: 'networkidle' });
  await oee.getByRole('heading', { name: 'Configuration Workspace' }).waitFor();
  const mappedTagCount = await oee.locator('tbody tr').count();
  await oee.getByLabel('Device Name').fill('IIoT Gateway · Docker integration');
  await oee.getByLabel('Security Policy').fill('None');
  await oee.getByLabel('Endpoint URL').fill('opc.tcp://iiot-gateway:7312/IIoTGateway');

  const nodes = [
    ['ns=2;s=DataAccess.DockerModbus.PlcSimulation.40020', 'Int32', 'Total_Count'],
    ['ns=2;s=DataAccess.DockerModbus.PlcSimulation.40022', 'Int32', 'Reject_Count'],
    ['ns=2;s=DataAccess.DockerModbus.PlcSimulation.40024', 'Int16', 'Machine_State'],
    ['ns=2;s=DataAccess.DockerModbus.PlcSimulation.40025', 'Int32', 'Counter_Epoch'],
  ];

  for (let index = 1; index < nodes.length; index += 1) {
    await oee.getByRole('button', { name: 'Add Node' }).click();
  }
  for (let index = 0; index < nodes.length; index += 1) {
    await oee.getByPlaceholder('Node ID').nth(index).fill(nodes[index][0]);
    await oee.getByPlaceholder('Data Type').nth(index).fill(nodes[index][1]);
    await oee.getByPlaceholder('Custom Tag').nth(index).fill(nodes[index][2]);
  }

  if (mappedTagCount === 0) {
    await oee.getByRole('button', { name: 'Test Connection' }).click();
    await oee.getByText('Connection test succeeded.').waitFor({ timeout: 15_000 });
    await oee.getByRole('button', { name: 'Save Configuration' }).click();
    await oee.getByText('OPC UA configuration saved.').waitFor({ timeout: 15_000 });
    await oee.getByText('4 tags', { exact: true }).waitFor({ timeout: 15_000 });
  }
  await savePage(oee, 'oee-04-data-sources.png');

  await oee.goto(`${urls.oee}/admin/processing`, { waitUntil: 'networkidle' });
  await oee.getByRole('heading', { name: 'Processing Rules' }).waitFor();
  await oee.getByPlaceholder('Equipment ID').first().fill('demo/automotive/main-conveyor');
  const oeeTagSelectors = oee.locator('select').all();
  const selectors = await oeeTagSelectors;
  if (selectors.length >= 3 && await selectors[0].locator('option').count() > 0) {
    await selectors[0].selectOption('Total_Count');
    await selectors[1].selectOption('Reject_Count');
    await selectors[2].selectOption('Machine_State');
  }
  await oee.locator('input[type="number"]').first().fill('2.5');
  await savePage(oee, 'oee-05-processing-rules.png');
} finally {
  await browser.close();
}

console.log(`Captured ${captured.length} image(s):`);
for (const file of captured) console.log(path.relative(repositoryRoot, file));
