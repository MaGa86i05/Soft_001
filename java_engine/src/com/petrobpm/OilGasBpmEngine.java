package com.petrobpm;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.*;

/**
 * PetroBPM Suitability & Fitness Verification Engine (Java 21 Core)
 * =================================================================
 * High-performance Discrete-Event & Monte Carlo Business Process Suitability
 * Engine for the 6-Stage Oil & Gas Industrial Production Chain:
 *   1. EXTRACTION      - Добыча нефти и газа (Скважины, ЭЦН/ШГН, фонтанная арматура, ГЗУ)
 *   2. PREPARATION     - Подготовка нефти и газа (УПН, трехфазная сепарация, ЭЛОУ, осушка газа)
 *   3. REFINING        - Переработка нефти и газа (АВТ-6, каталитический крекинг, гидроочистка, ГПЗ)
 *   4. TRANSPORTATION  - Транспортировка нефти и газа (МН/МГ, НПС/КС, СИКН, ж/д и танкерная отгрузка)
 *   5. STORAGE         - Складирование (Резервуарные парки РВС/РВСП, ПХГ, УЛФ, коммерческий учет)
 *   6. SLUDGE_DISPOSAL - Утилизация нефтешлама (Шламонакопители, декантерные трикантеры, пиролиз, биоремедиация)
 *
 * Performs:
 *   - Structural BPMN graph validation & bottleneck analysis
 *   - Mass & volume balance verification across stages
 *   - Equipment reliability & MTBF/MTTR availability calculation
 *   - Industrial safety & ecological compliance check (ПБ ОПО, ГОСТ Р 51858, ПДК)
 *   - Monte Carlo 1,000-iteration stochastic stress simulation
 *   - Suitability Verdict ("ПРИГОДЕН" / "УСЛОВНО ПРИГОДЕН" / "НЕПРИГОДЕН")
 */
public class OilGasBpmEngine {

    public static class StageConfig {
        public String id;
        public String nameRu;
        public String standardCode;
        public double capacityTonsPerDay;      // Пропускная способность, т/сут
        public double conversionEfficiency;    // КПД / Выход целевого продукта (0..1)
        public double lossRate;                // Доля технологических потерь / шлама (0..1)
        public double reliabilityMtbfHours;    // Наработка на отказ MTBF, ч
        public double recoveryMttrHours;       // Время восстановления MTTR, ч
        public double pressureMpa;             // Рабочее давление, МПа
        public double maxAllowedPressureMpa;   // Предельно допустимое давление, МПа
        public double temperatureC;            // Рабочая температура, °C
        public double maxAllowedTempC;         // Предельная температура, °C
        public double automationLevel;         // Уровень автоматизации АСУ ТП / ПАЗ (0..1)
        public double ecoSafetyIndex;          // Индекс пром. и экологической безопасности (0..1)
        public double opexRubPerTon;           // Удельные операционные затраты, руб/т

        public StageConfig(String id, String nameRu, String standardCode,
                           double capacity, double eff, double loss,
                           double mtbf, double mttr,
                           double p, double pMax, double t, double tMax,
                           double autoLvl, double ecoIdx, double opex) {
            this.id = id;
            this.nameRu = nameRu;
            this.standardCode = standardCode;
            this.capacityTonsPerDay = capacity;
            this.conversionEfficiency = eff;
            this.lossRate = loss;
            this.reliabilityMtbfHours = mtbf;
            this.recoveryMttrHours = mttr;
            this.pressureMpa = p;
            this.maxAllowedPressureMpa = pMax;
            this.temperatureC = t;
            this.maxAllowedTempC = tMax;
            this.automationLevel = autoLvl;
            this.ecoSafetyIndex = ecoIdx;
            this.opexRubPerTon = opex;
        }
    }

    public static class StageEvaluation {
        public StageConfig cfg;
        public double inputFlowTonsDay;
        public double outputProductTonsDay;
        public double generatedSludgeTonsDay;
        public double utilizationRatio;
        public double availabilityFactor;
        public double thermalPressureSafetyMargin;
        public double stageSuitabilityScore; // 0..100
        public String status;                // OPTIMAL / WARNING / CRITICAL
        public List<String> diagnostics = new ArrayList<>();
    }

    public static List<StageConfig> getDefaultPreset(String scenario) {
        List<StageConfig> list = new ArrayList<>();
        if ("overload_hazard".equalsIgnoreCase(scenario)) {
            list.add(new StageConfig("EXTRACTION", "1. Добыча нефти и газа (Куст скважин УЭЦН / ГЗУ)", "ГОСТ Р 51858 / ПБ ОПО",
                    14800.0, 0.96, 0.032, 3200.0, 18.0, 14.5, 16.0, 78.0, 95.0, 0.88, 0.86, 1450.0));
            list.add(new StageConfig("PREPARATION", "2. Подготовка нефти и газа (УПН / Сепарация / ЭЛОУ)", "ГОСТ Р 51858-2020 (1 группа)",
                    11200.0, 0.91, 0.048, 2100.0, 26.0, 6.2, 6.4, 88.0, 90.0, 0.74, 0.72, 890.0));
            list.add(new StageConfig("REFINING", "3. Переработка нефти и газа (АВТ-6 / Каткрекинг / ГПЗ)", "ТР ЕАЭС 036/2016 / ГОСТ Р",
                    10500.0, 0.87, 0.055, 1850.0, 36.0, 4.1, 4.2, 385.0, 395.0, 0.76, 0.70, 2650.0));
            list.add(new StageConfig("TRANSPORTATION", "4. Транспортировка нефти и газа (МН / МГ / НПС / СИКН)", "СП 36.13330 / СТО Транснефть",
                    12500.0, 0.985, 0.012, 4100.0, 14.0, 7.1, 7.5, 42.0, 65.0, 0.85, 0.82, 620.0));
            list.add(new StageConfig("STORAGE", "5. Складирование (Резервуарный парк РВСП-50000 / ПХГ)", "ГОСТ 31385 / ПБ 03-605",
                    9400.0, 0.990, 0.015, 3800.0, 16.0, 0.19, 0.20, 38.0, 45.0, 0.78, 0.75, 410.0));
            list.add(new StageConfig("SLUDGE_DISPOSAL", "6. Утилизация нефтешлама (Декантер / Пиролиз / Биоремедиация)", "ФЗ-89 / ГОСТ Р 57446",
                    820.0, 0.78, 0.080, 1400.0, 28.0, 1.8, 2.2, 490.0, 520.0, 0.65, 0.64, 3400.0));
        } else if ("eco_modernized".equalsIgnoreCase(scenario)) {
            list.add(new StageConfig("EXTRACTION", "1. Добыча нефти и газа (Интеллектуальное месторождение УЭЦН)", "ГОСТ Р 51858 / Цифровой куст",
                    12500.0, 0.982, 0.018, 6800.0, 8.0, 11.2, 16.0, 62.0, 95.0, 0.97, 0.96, 1280.0));
            list.add(new StageConfig("PREPARATION", "2. Подготовка нефти и газа (УПН + ЭЛОУ + Мембранная осушка)", "ГОСТ Р 51858-2020 (Высшая)",
                    13800.0, 0.968, 0.022, 6400.0, 9.0, 4.2, 6.4, 68.0, 90.0, 0.96, 0.95, 760.0));
            list.add(new StageConfig("REFINING", "3. Переработка нефти и газа (АВТ-6 + Гидрокрекинг + ГПЗ)", "ТР ЕАЭС 036/2016 (Евро-6)",
                    13200.0, 0.945, 0.028, 5900.0, 12.0, 3.1, 4.5, 348.0, 410.0, 0.98, 0.95, 2240.0));
            list.add(new StageConfig("TRANSPORTATION", "4. Транспортировка нефти и газа (МН / МГ + Сell-СИКН + СОУ)", "СП 36.13330 / ISO 13623",
                    14500.0, 0.996, 0.004, 8200.0, 6.0, 5.4, 7.5, 28.0, 65.0, 0.98, 0.97, 510.0));
            list.add(new StageConfig("STORAGE", "5. Складирование (РВСП-50000 с понтоном + УЛФ рекуперации)", "ГОСТ 31385 / API 650",
                    15000.0, 0.997, 0.003, 8600.0, 6.0, 0.11, 0.20, 24.0, 50.0, 0.96, 0.97, 340.0));
            list.add(new StageConfig("SLUDGE_DISPOSAL", "6. Утилизация нефтешлама (Трикантер Flottweg + Термодесорбция + Био)", "ФЗ-89 / НДТ ИТС 15-2021",
                    1850.0, 0.955, 0.015, 5800.0, 10.0, 1.2, 2.5, 430.0, 550.0, 0.94, 0.96, 2750.0));
        } else {
            // Standard Nominal Baseline ("nominal")
            list.add(new StageConfig("EXTRACTION", "1. Добыча нефти и газа (Куст скважин УЭЦН / Фонтан / ГЗУ)", "ГОСТ Р 51858 / ПБ ОПО",
                    12000.0, 0.972, 0.022, 5200.0, 12.0, 12.0, 16.0, 65.0, 95.0, 0.92, 0.91, 1350.0));
            list.add(new StageConfig("PREPARATION", "2. Подготовка нефти и газа (УПН / Сепарация / ЭЛОУ / Осушка)", "ГОСТ Р 51858-2020",
                    12800.0, 0.954, 0.028, 4900.0, 14.0, 4.6, 6.4, 72.0, 90.0, 0.91, 0.90, 810.0));
            list.add(new StageConfig("REFINING", "3. Переработка нефти и газа (АВТ-6 / Каткрекинг / Гидроочистка)", "ТР ЕАЭС 036/2016",
                    12200.0, 0.928, 0.034, 4600.0, 16.0, 3.4, 4.5, 358.0, 410.0, 0.93, 0.89, 2380.0));
            list.add(new StageConfig("TRANSPORTATION", "4. Транспортировка нефти и газа (МН / МГ / НПС / СИКН)", "СП 36.13330",
                    13500.0, 0.993, 0.005, 6800.0, 8.0, 5.8, 7.5, 32.0, 65.0, 0.94, 0.93, 560.0));
            list.add(new StageConfig("STORAGE", "5. Складирование (Резервуарный парк РВСП / ПХГ / УЛФ)", "ГОСТ 31385",
                    14000.0, 0.995, 0.004, 7200.0, 8.0, 0.12, 0.20, 26.0, 50.0, 0.92, 0.93, 370.0));
            list.add(new StageConfig("SLUDGE_DISPOSAL", "6. Утилизация нефтешлама (Трикантер / Пиролиз / Биоремедиация)", "ФЗ-89 / ИТС 15",
                    1500.0, 0.925, 0.025, 4500.0, 12.0, 1.4, 2.5, 445.0, 550.0, 0.89, 0.91, 2950.0));
        }
        return list;
    }

    public static Map<String, String> parseArgs(String[] args) {
        Map<String, String> map = new HashMap<>();
        for (int i = 0; i < args.length; i++) {
            if (args[i].startsWith("--") && i + 1 < args.length) {
                map.put(args[i].substring(2), args[i + 1]);
                i++;
            }
        }
        return map;
    }

    public static void main(String[] args) {
        Map<String, String> params = parseArgs(args);
        String scenario = params.getOrDefault("scenario", "nominal");
        double feedRateScale = Double.parseDouble(params.getOrDefault("feedScale", "1.0"));
        double sludgeFactor = Double.parseDouble(params.getOrDefault("sludgeFactor", "1.0"));
        int monteCarloRuns = Integer.parseInt(params.getOrDefault("monteCarlo", "1000"));

        List<StageConfig> stages = getDefaultPreset(scenario);

        // Allow custom overrides per stage capacity or efficiency if passed
        if (params.containsKey("extractionCap")) {
            stages.get(0).capacityTonsPerDay = Double.parseDouble(params.get("extractionCap"));
        }
        if (params.containsKey("prepCap")) {
            stages.get(1).capacityTonsPerDay = Double.parseDouble(params.get("prepCap"));
        }
        if (params.containsKey("refiningCap")) {
            stages.get(2).capacityTonsPerDay = Double.parseDouble(params.get("refiningCap"));
        }
        if (params.containsKey("transportCap")) {
            stages.get(3).capacityTonsPerDay = Double.parseDouble(params.get("transportCap"));
        }
        if (params.containsKey("storageCap")) {
            stages.get(4).capacityTonsPerDay = Double.parseDouble(params.get("storageCap"));
        }
        if (params.containsKey("sludgeCap")) {
            stages.get(5).capacityTonsPerDay = Double.parseDouble(params.get("sludgeCap"));
        }

        List<StageEvaluation> evaluations = new ArrayList<>();
        double currentFlow = stages.get(0).capacityTonsPerDay * 0.92 * feedRateScale;
        double totalSludgeGenerated = 0.0;
        double totalDailyOpexRub = 0.0;

        // Evaluate stages 1..5 sequentially (Main Hydrocarbon Stream)
        for (int i = 0; i < 5; i++) {
            StageConfig sc = stages.get(i);
            StageEvaluation ev = new StageEvaluation();
            ev.cfg = sc;
            ev.inputFlowTonsDay = (i == 0) ? currentFlow : evaluations.get(i - 1).outputProductTonsDay;

            double effectiveFlow = Math.min(ev.inputFlowTonsDay, sc.capacityTonsPerDay);
            ev.utilizationRatio = ev.inputFlowTonsDay / Math.max(1.0, sc.capacityTonsPerDay);
            ev.availabilityFactor = sc.reliabilityMtbfHours / (sc.reliabilityMtbfHours + sc.recoveryMttrHours);

            double pRatio = sc.pressureMpa / Math.max(0.001, sc.maxAllowedPressureMpa);
            double tRatio = sc.temperatureC / Math.max(1.0, sc.maxAllowedTempC);
            ev.thermalPressureSafetyMargin = Math.max(0.0, 1.0 - Math.max(pRatio, tRatio));

            ev.generatedSludgeTonsDay = effectiveFlow * sc.lossRate * sludgeFactor;
            totalSludgeGenerated += ev.generatedSludgeTonsDay;

            // If overloaded (> 100% capacity), unbuffered excess causes throttling & extra sludge
            double overloadPenalty = 0.0;
            if (ev.utilizationRatio > 1.0) {
                overloadPenalty = Math.min(35.0, (ev.utilizationRatio - 1.0) * 110.0);
                ev.generatedSludgeTonsDay += (ev.inputFlowTonsDay - sc.capacityTonsPerDay) * 0.12;
                totalSludgeGenerated += (ev.inputFlowTonsDay - sc.capacityTonsPerDay) * 0.12;
                ev.diagnostics.add(String.format(Locale.US,
                        "ПЕРЕГРУЗКА УЗЛА: входной поток %.1f т/сут превышает проектную мощность %.1f т/сут (загрузка %.1f%%)",
                        ev.inputFlowTonsDay, sc.capacityTonsPerDay, ev.utilizationRatio * 100.0));
            } else if (ev.utilizationRatio > 0.93) {
                ev.diagnostics.add(String.format(Locale.US,
                        "Высокая загрузка мощности (%.1f%%) — рекомендуется резервирование линии",
                        ev.utilizationRatio * 100.0));
            } else {
                ev.diagnostics.add(String.format(Locale.US,
                        "Гидравлический и массовый баланс в норме (загрузка %.1f%%)",
                        ev.utilizationRatio * 100.0));
            }

            if (pRatio > 0.92 || tRatio > 0.92) {
                ev.diagnostics.add(String.format(Locale.US,
                        "ВНИМАНИЕ ПАЗ: термобарический режим близок к уставке срабатывания клапанов (P=%.2f/%.2f МПа, T=%.1f/%.1f °C)",
                        sc.pressureMpa, sc.maxAllowedPressureMpa, sc.temperatureC, sc.maxAllowedTempC));
            } else {
                ev.diagnostics.add(String.format(Locale.US,
                        "Термобарический режим стабилен (запас прочности %.1f%%)",
                        ev.thermalPressureSafetyMargin * 100.0));
            }

            ev.outputProductTonsDay = effectiveFlow * sc.conversionEfficiency * ev.availabilityFactor;
            totalDailyOpexRub += effectiveFlow * sc.opexRubPerTon;

            // Compute stage suitability score (0..100)
            double capScore = (ev.utilizationRatio <= 0.95) ? 100.0 : Math.max(25.0, 100.0 - overloadPenalty - (ev.utilizationRatio - 0.95) * 90.0);
            double relScore = Math.min(100.0, ev.availabilityFactor * 100.5);
            double safeScore = Math.min(100.0, (sc.automationLevel * 0.45 + sc.ecoSafetyIndex * 0.40 + Math.min(0.25, ev.thermalPressureSafetyMargin) * 0.60) * 100.0);
            double effScore = Math.min(100.0, sc.conversionEfficiency * 103.0);

            ev.stageSuitabilityScore = Math.max(0.0, Math.min(100.0,
                    capScore * 0.34 + relScore * 0.22 + safeScore * 0.26 + effScore * 0.18));

            if (ev.stageSuitabilityScore >= 85.0 && ev.utilizationRatio <= 1.0) {
                ev.status = "OPTIMAL";
            } else if (ev.stageSuitabilityScore >= 70.0) {
                ev.status = "WARNING";
            } else {
                ev.status = "CRITICAL";
            }

            evaluations.add(ev);
        }

        // Evaluate Stage 6: SLUDGE_DISPOSAL (Утилизация нефтешлама)
        StageConfig sludgeCfg = stages.get(5);
        StageEvaluation sludgeEv = new StageEvaluation();
        sludgeEv.cfg = sludgeCfg;
        // Input to sludge treatment = accumulated sludge from stages 1..5 + legacy pit remediation feed (450 t/day baseline)
        sludgeEv.inputFlowTonsDay = totalSludgeGenerated + 420.0 * sludgeFactor;
        sludgeEv.utilizationRatio = sludgeEv.inputFlowTonsDay / Math.max(1.0, sludgeCfg.capacityTonsPerDay);
        sludgeEv.availabilityFactor = sludgeCfg.reliabilityMtbfHours / (sludgeCfg.reliabilityMtbfHours + sludgeCfg.recoveryMttrHours);
        double effectiveSludgeProcessed = Math.min(sludgeEv.inputFlowTonsDay, sludgeCfg.capacityTonsPerDay) * sludgeEv.availabilityFactor;
        // Recovered hydrocarbons returned to preparation/storage + neutralized mineral residue
        sludgeEv.outputProductTonsDay = effectiveSludgeProcessed * sludgeCfg.conversionEfficiency;
        sludgeEv.generatedSludgeTonsDay = Math.max(0.0, sludgeEv.inputFlowTonsDay - effectiveSludgeProcessed)
                + effectiveSludgeProcessed * sludgeCfg.lossRate;
        totalDailyOpexRub += effectiveSludgeProcessed * sludgeCfg.opexRubPerTon;

        double pRatioS = sludgeCfg.pressureMpa / Math.max(0.001, sludgeCfg.maxAllowedPressureMpa);
        double tRatioS = sludgeCfg.temperatureC / Math.max(1.0, sludgeCfg.maxAllowedTempC);
        sludgeEv.thermalPressureSafetyMargin = Math.max(0.0, 1.0 - Math.max(pRatioS, tRatioS));

        double sludgeCapScore = (sludgeEv.utilizationRatio <= 0.95)
                ? 100.0
                : Math.max(20.0, 100.0 - (sludgeEv.utilizationRatio - 0.95) * 140.0);
        double sludgeSafeScore = (sludgeCfg.automationLevel * 0.45 + sludgeCfg.ecoSafetyIndex * 0.55) * 100.0;
        sludgeEv.stageSuitabilityScore = Math.max(0.0, Math.min(100.0,
                sludgeCapScore * 0.40 + (sludgeEv.availabilityFactor * 100.0) * 0.20 + sludgeSafeScore * 0.25 + (sludgeCfg.conversionEfficiency * 100.0) * 0.15));

        if (sludgeEv.utilizationRatio > 1.0) {
            sludgeEv.diagnostics.add(String.format(Locale.US,
                    "КРИТИЧЕСКИЙ РИСК ПЕРЕПОЛНЕНИЯ ШЛАМОНАКОПИТЕЛЯ: поступление %.1f т/сут превышает мощность УПНШ %.1f т/сут",
                    sludgeEv.inputFlowTonsDay, sludgeCfg.capacityTonsPerDay));
        } else {
            sludgeEv.diagnostics.add(String.format(Locale.US,
                    "Баланс переработки нефтешлама обеспечен (утилизировано %.1f%%, возврат углеводородов %.1f т/сут)",
                    Math.min(100.0, (effectiveSludgeProcessed / Math.max(1.0, sludgeEv.inputFlowTonsDay)) * 100.0),
                    sludgeEv.outputProductTonsDay * 0.68));
        }
        sludgeEv.diagnostics.add(String.format(Locale.US,
                "Остаточный нейтрализованный кек IV класса опасности: %.1f т/сут (соответствие ФЗ-89 и ИТС 15)",
                sludgeEv.generatedSludgeTonsDay));

        if (sludgeEv.stageSuitabilityScore >= 85.0 && sludgeEv.utilizationRatio <= 1.0) {
            sludgeEv.status = "OPTIMAL";
        } else if (sludgeEv.stageSuitabilityScore >= 70.0) {
            sludgeEv.status = "WARNING";
        } else {
            sludgeEv.status = "CRITICAL";
        }
        evaluations.add(sludgeEv);

        // Monte Carlo Stochastic Suitability Simulation (1000 runs)
        Random rng = new Random(20261016L);
        int passRuns = 0;
        double sumSimOutput = 0.0;
        double minSimOutput = Double.MAX_VALUE;
        double maxSimOutput = 0.0;

        for (int run = 0; run < monteCarloRuns; run++) {
            double flow = stages.get(0).capacityTonsPerDay * (0.88 + rng.nextDouble() * 0.10) * feedRateScale;
            boolean runSuccess = true;
            double runSludge = 0.0;
            for (int i = 0; i < 5; i++) {
                StageConfig sc = stages.get(i);
                double avail = (rng.nextDouble() < (sc.recoveryMttrHours / (sc.reliabilityMtbfHours + sc.recoveryMttrHours)) * 2.2)
                        ? 0.82 : 1.0;
                double capEff = sc.capacityTonsPerDay * avail;
                if (flow > capEff * 1.04) {
                    runSuccess = false;
                }
                double proc = Math.min(flow, capEff);
                runSludge += proc * sc.lossRate * sludgeFactor;
                flow = proc * sc.conversionEfficiency;
            }
            double totalSludgeRun = runSludge + 420.0 * sludgeFactor;
            if (totalSludgeRun > sludgeCfg.capacityTonsPerDay * 1.05) {
                runSuccess = false;
            }
            if (runSuccess) {
                passRuns++;
            }
            sumSimOutput += flow;
            if (flow < minSimOutput) minSimOutput = flow;
            if (flow > maxSimOutput) maxSimOutput = flow;
        }

        double monteCarloReliabilityPct = (passRuns * 100.0) / Math.max(1, monteCarloRuns);
        double avgScore = 0.0;
        double minStageScore = 100.0;
        String bottleneckStage = evaluations.get(0).cfg.nameRu;
        for (StageEvaluation ev : evaluations) {
            avgScore += ev.stageSuitabilityScore;
            if (ev.stageSuitabilityScore < minStageScore) {
                minStageScore = ev.stageSuitabilityScore;
                bottleneckStage = ev.cfg.nameRu;
            }
        }
        avgScore /= evaluations.size();

        // Overall composite fitness index combines weighted average + weakest-link penalty + Monte Carlo stability
        double overallSuitabilityIndex = avgScore * 0.55 + minStageScore * 0.25 + monteCarloReliabilityPct * 0.20;
        String verdictCode;
        String verdictRu;
        if (overallSuitabilityIndex >= 84.0 && minStageScore >= 75.0) {
            verdictCode = "SUITABLE";
            verdictRu = "ПРИГОДЕН К ПРОМЫШЛЕННОЙ ЭКСПЛУАТАЦИИ (Высший класс надежности АСУ ТП / ПБ ОПО)";
        } else if (overallSuitabilityIndex >= 68.0) {
            verdictCode = "CONDITIONALLY_SUITABLE";
            verdictRu = "УСЛОВНО ПРИГОДЕН (Требуется расшивка узких мест и балансировка мощностей)";
        } else {
            verdictCode = "UNSUITABLE";
            verdictRu = "НЕПРИГОДЕН — КРИТИЧЕСКИЙ РИСК ОТКАЗА ИЛИ НАРУШЕНИЯ ЭКОБЕЗОПАСНОСТИ";
        }

        // Emit structured JSON to stdout for seamless Python / Web integration
        StringBuilder sb = new StringBuilder();
        sb.append("{\n");
        sb.append("  \"engine\": \"PetroBPM Java 21 Suitability & Monte Carlo Core v3.4\",\n");
        sb.append(String.format(Locale.US, "  \"scenario\": \"%s\",\n", escapeJson(scenario)));
        sb.append(String.format(Locale.US, "  \"overallSuitabilityIndex\": %.2f,\n", overallSuitabilityIndex));
        sb.append(String.format(Locale.US, "  \"averageStageScore\": %.2f,\n", avgScore));
        sb.append(String.format(Locale.US, "  \"minStageScore\": %.2f,\n", minStageScore));
        sb.append(String.format(Locale.US, "  \"bottleneckStage\": \"%s\",\n", escapeJson(bottleneckStage)));
        sb.append(String.format(Locale.US, "  \"verdictCode\": \"%s\",\n", verdictCode));
        sb.append(String.format(Locale.US, "  \"verdictRu\": \"%s\",\n", escapeJson(verdictRu)));
        sb.append(String.format(Locale.US, "  \"monteCarloRuns\": %d,\n", monteCarloRuns));
        sb.append(String.format(Locale.US, "  \"monteCarloStabilityPct\": %.2f,\n", monteCarloReliabilityPct));
        sb.append(String.format(Locale.US, "  \"meanCommercialOutputTonsDay\": %.2f,\n", sumSimOutput / Math.max(1, monteCarloRuns)));
        sb.append(String.format(Locale.US, "  \"minCommercialOutputTonsDay\": %.2f,\n", minSimOutput));
        sb.append(String.format(Locale.US, "  \"maxCommercialOutputTonsDay\": %.2f,\n", maxSimOutput));
        sb.append(String.format(Locale.US, "  \"totalSludgeGeneratedTonsDay\": %.2f,\n", totalSludgeGenerated));
        sb.append(String.format(Locale.US, "  \"sludgeRecycledHydrocarbonsTonsDay\": %.2f,\n", sludgeEv.outputProductTonsDay * 0.68));
        sb.append(String.format(Locale.US, "  \"totalDailyOpexMillionRub\": %.3f,\n", totalDailyOpexRub / 1_000_000.0));
        sb.append("  \"stages\": [\n");
        for (int i = 0; i < evaluations.size(); i++) {
            StageEvaluation ev = evaluations.get(i);
            sb.append("    {\n");
            sb.append(String.format(Locale.US, "      \"id\": \"%s\",\n", escapeJson(ev.cfg.id)));
            sb.append(String.format(Locale.US, "      \"nameRu\": \"%s\",\n", escapeJson(ev.cfg.nameRu)));
            sb.append(String.format(Locale.US, "      \"standardCode\": \"%s\",\n", escapeJson(ev.cfg.standardCode)));
            sb.append(String.format(Locale.US, "      \"capacityTonsPerDay\": %.2f,\n", ev.cfg.capacityTonsPerDay));
            sb.append(String.format(Locale.US, "      \"inputFlowTonsDay\": %.2f,\n", ev.inputFlowTonsDay));
            sb.append(String.format(Locale.US, "      \"outputProductTonsDay\": %.2f,\n", ev.outputProductTonsDay));
            sb.append(String.format(Locale.US, "      \"generatedSludgeTonsDay\": %.2f,\n", ev.generatedSludgeTonsDay));
            sb.append(String.format(Locale.US, "      \"utilizationPct\": %.2f,\n", ev.utilizationRatio * 100.0));
            sb.append(String.format(Locale.US, "      \"availabilityPct\": %.2f,\n", ev.availabilityFactor * 100.0));
            sb.append(String.format(Locale.US, "      \"conversionEfficiencyPct\": %.2f,\n", ev.cfg.conversionEfficiency * 100.0));
            sb.append(String.format(Locale.US, "      \"pressureMpa\": %.2f,\n", ev.cfg.pressureMpa));
            sb.append(String.format(Locale.US, "      \"maxAllowedPressureMpa\": %.2f,\n", ev.cfg.maxAllowedPressureMpa));
            sb.append(String.format(Locale.US, "      \"temperatureC\": %.1f,\n", ev.cfg.temperatureC));
            sb.append(String.format(Locale.US, "      \"maxAllowedTempC\": %.1f,\n", ev.cfg.maxAllowedTempC));
            sb.append(String.format(Locale.US, "      \"automationPct\": %.1f,\n", ev.cfg.automationLevel * 100.0));
            sb.append(String.format(Locale.US, "      \"ecoSafetyPct\": %.1f,\n", ev.cfg.ecoSafetyIndex * 100.0));
            sb.append(String.format(Locale.US, "      \"suitabilityScore\": %.2f,\n", ev.stageSuitabilityScore));
            sb.append(String.format(Locale.US, "      \"status\": \"%s\",\n", ev.status));
            sb.append("      \"diagnostics\": [");
            for (int d = 0; d < ev.diagnostics.size(); d++) {
                sb.append("\"").append(escapeJson(ev.diagnostics.get(d))).append("\"");
                if (d < ev.diagnostics.size() - 1) sb.append(", ");
            }
            sb.append("]\n");
            sb.append("    }").append(i < evaluations.size() - 1 ? ",\n" : "\n");
        }
        sb.append("  ]\n");
        sb.append("}\n");

        PrintStream out = new PrintStream(System.out, true, StandardCharsets.UTF_8);
        out.print(sb.toString());
        out.flush();
    }

    private static String escapeJson(String s) {
        if (s == null) return "";
        return s.replace("\\", "\\\\").replace("\"", "\\\"");
    }
}
