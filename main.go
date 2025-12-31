package main

import (
	"fmt"
	"log"
	"os"
	"path/filepath"
	"regexp"
	"strings"
)

func main() {
	fmt.Println("╔══════════════════════════════════════════════╗")
	fmt.Println("║           err_x509 v1.1 - TLS Safe           ║")
	fmt.Println("║    SSL Certificate Verification Disabler     ║")
	fmt.Println("╚══════════════════════════════════════════════╝")
	fmt.Println()
	fmt.Println("📝 Добавляет 'skip-cert-verify: true' к прокси")
	fmt.Println("🛡️ Сохраняет все TLS/SSL параметры")
	fmt.Println("⚡ Быстро и безопасно")
	fmt.Println()

	// Конфигурационные файлы
	inputFile := "x509_no_fix.yaml"
	outputFile := "x509_fixed.yaml"
	backupFile := "x509_no_fix.yaml.backup"

	// Проверка входного файла
	if _, err := os.Stat(inputFile); os.IsNotExist(err) {
		fmt.Println("❌ ОШИБКА: Файл конфигурации не найден!")
		fmt.Println()
		fmt.Println("📋 ИНСТРУКЦИЯ:")
		fmt.Println("1. Поместите ваш конфиг в файл '" + inputFile + "'")
		fmt.Println("2. Файл должен быть в той же папке, где находится программа")
		fmt.Println("3. Запустите программу снова")
		fmt.Println()
		fmt.Println("Пример файла " + inputFile + ":")
		fmt.Println("proxies:")
		fmt.Println("  - { name: Server1, type: trojan, server: s1.com, port: 443, password: pass1 }")
		fmt.Println("  - { name: Server2, type: vmess, server: s2.com, port: 443, uuid: xxxxx }")
		fmt.Println()
		fmt.Scanln()
		os.Exit(1)
	}

	// Чтение файла
	fmt.Printf("📖 Чтение файла: %s\n", inputFile)
	data, err := os.ReadFile(inputFile)
	if err != nil {
		log.Fatalf("❌ Ошибка чтения файла: %v", err)
	}

	originalContent := string(data)
	content := originalContent
	proxyCount := 0
	alreadyHasSkipCount := 0

	// Создаем резервную копию
	fmt.Printf("💾 Создание резервной копии: %s\n", backupFile)
	if err := os.WriteFile(backupFile, data, 0644); err != nil {
		fmt.Printf("⚠️  Не удалось создать резервную копию: %v\n", err)
	} else {
		fmt.Println("✅ Резервная копия создана")
	}

	fmt.Println()
	fmt.Println("🔍 Поиск прокси для обработки...")

	// ШАГ 1: Обработка компактного формата { ... }
	compactProxyPattern := regexp.MustCompile(`(\s*-\s*\{[^}]+\})`)
	compactMatches := compactProxyPattern.FindAllStringSubmatchIndex(content, -1)

	if len(compactMatches) > 0 {
		fmt.Printf("📋 Найдено прокси в компактном формате: %d\n", len(compactMatches))

		// Обрабатываем с конца, чтобы не сбивать индексы
		for i := len(compactMatches) - 1; i >= 0; i-- {
			start, end := compactMatches[i][0], compactMatches[i][1]
			proxyStr := content[start:end]

			// Проверяем, что это прокси (имеет минимальный набор полей)
			if strings.Contains(proxyStr, "name:") &&
				strings.Contains(proxyStr, "server:") &&
				strings.Contains(proxyStr, "port:") {

				// Проверяем наличие skip-cert-verify
				if strings.Contains(proxyStr, "skip-cert-verify:") {
					alreadyHasSkipCount++
					continue
				}

				// Удаляем возможную запятую в конце перед }
				cleanedProxy := strings.TrimSpace(proxyStr)
				if strings.HasSuffix(cleanedProxy, ", }") {
					cleanedProxy = strings.TrimSuffix(cleanedProxy, ", }")
					cleanedProxy = cleanedProxy + " }"
				}

				// Добавляем skip-cert-verify: true перед закрывающей скобкой
				newProxy := strings.TrimSuffix(cleanedProxy, "}")
				newProxy = newProxy + ", skip-cert-verify: true }"

				// Заменяем в содержимом
				content = content[:start] + newProxy + content[end:]
				proxyCount++
			}
		}
	}

	// ШАГ 2: Обработка многострочного формата (если нужно)
	if proxyCount == 0 && len(compactMatches) == 0 {
		fmt.Println("🔍 Поиск прокси в многострочном формате...")

		lines := strings.Split(originalContent, "\n")
		var resultLines []string
		inProxiesSection := false
		proxiesStarted := false

		for _, line := range lines {
			trimmed := strings.TrimSpace(line)

			// Начало секции proxies
			if trimmed == "proxies:" {
				inProxiesSection = true
				proxiesStarted = true
				resultLines = append(resultLines, line)
				continue
			}

			// Если мы в секции proxies
			if inProxiesSection {
				// Проверяем, закончилась ли секция proxies
				if trimmed != "" && !strings.HasPrefix(trimmed, "-") &&
					!strings.HasPrefix(trimmed, "#") && !strings.HasPrefix(trimmed, " ") &&
					proxiesStarted {
					inProxiesSection = false
				}

				// Если это строка с прокси
				if strings.HasPrefix(trimmed, "-") && strings.Contains(trimmed, "name:") {
					// Проверяем наличие skip-cert-verify
					if strings.Contains(line, "skip-cert-verify:") {
						alreadyHasSkipCount++
						resultLines = append(resultLines, line)
						continue
					}

					// Для многострочного формата добавляем новую строку
					resultLines = append(resultLines, line)
					resultLines = append(resultLines, "  skip-cert-verify: true")
					proxyCount++
					continue
				}
			}

			resultLines = append(resultLines, line)
		}

		if proxyCount > 0 {
			content = strings.Join(resultLines, "\n")
		}
	}

	// Запись результата
	fmt.Println()
	if proxyCount > 0 || alreadyHasSkipCount > 0 {
		fmt.Printf("📊 СТАТИСТИКА ОБРАБОТКИ:\n")
		fmt.Printf("   ✅ Обработано прокси: %d\n", proxyCount)
		fmt.Printf("   ⚡ Уже имели skip-cert-verify: %d\n", alreadyHasSkipCount)
		fmt.Printf("   📄 Всего найдено прокси: %d\n", proxyCount+alreadyHasSkipCount)
	} else {
		fmt.Println("⚠️  ВНИМАНИЕ: Прокси не найдены!")
		fmt.Println()
		fmt.Println("Возможные причины:")
		fmt.Println("1. Файл уже содержит skip-cert-verify: true для всех прокси")
		fmt.Println("2. Формат файла не распознан")
		fmt.Println("3. В файле нет секции 'proxies:'")
		fmt.Println()
		fmt.Println("Поддерживаемые форматы:")
		fmt.Println("• Компактный: - { name: ..., server: ..., port: ... }")
		fmt.Println("• Многострочный (частично)")
	}

	// Сохранение результата
	fmt.Println()
	fmt.Printf("💾 Сохранение результата: %s\n", outputFile)
	err = os.WriteFile(outputFile, []byte(content), 0644)
	if err != nil {
		log.Fatalf("❌ Ошибка сохранения файла: %v", err)
	}

	// Показ путей к файлам
	absInput, _ := filepath.Abs(inputFile)
	absOutput, _ := filepath.Abs(outputFile)

	fmt.Println()
	fmt.Println("✅ ВЫПОЛНЕНО УСПЕШНО!")
	fmt.Println("══════════════════════════════════════════════")
	fmt.Printf("📂 Исходный файл: %s\n", absInput)
	fmt.Printf("📂 Результат: %s\n", absOutput)
	if _, err := os.Stat(backupFile); err == nil {
		absBackup, _ := filepath.Abs(backupFile)
		fmt.Printf("📂 Резервная копия: %s\n", absBackup)
	}
	fmt.Println("══════════════════════════════════════════════")

	// Показ примера изменений
	if proxyCount > 0 {
		fmt.Println()
		fmt.Println("🔍 ПРИМЕР ИЗМЕНЕНИЙ:")
		fmt.Println("══════════════════════════════════════════════")

		// Находим первый измененный прокси для примера
		oldLines := strings.Split(originalContent, "\n")
		newLines := strings.Split(content, "\n")

		for i := 0; i < len(oldLines) && i < len(newLines); i++ {
			if oldLines[i] != newLines[i] && strings.Contains(newLines[i], "skip-cert-verify:") {
				// Находим соответствующий старый прокси
				for j := i; j >= 0; j-- {
					if strings.Contains(oldLines[j], "name:") && strings.Contains(oldLines[j], "server:") {
						fmt.Println("ДО: " + strings.TrimSpace(oldLines[j]))
						fmt.Println("ПОСЛЕ: " + strings.TrimSpace(newLines[i]))
						break
					}
				}
				break
			}
		}
		fmt.Println("══════════════════════════════════════════════")
	}

	fmt.Println("🚀 Используйте файл '" + outputFile + "' в вашем клиенте")
	fmt.Println()
	fmt.Scanln()
}
