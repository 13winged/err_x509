package main

import (
	"fmt"
	"log"
	"os"
	"path/filepath"
	"strings"
)

func main() {
	fmt.Println("=== X509 SSL Certificate Fix Tool ===")
	fmt.Println("Добавляет skip-cert-verify: true ко всем прокси в конфигурации")
	fmt.Println()

	inputFile := "x509_no_fix.yaml"
	outputFile := "x509_fixed.yaml"

	if _, err := os.Stat(inputFile); os.IsNotExist(err) {
		log.Fatalf("❌ Файл '%s' не найден!\nПоместите ваш конфиг в файл с именем '%s' в ту же папку, где находится программа.", inputFile, inputFile)
	}

	data, err := os.ReadFile(inputFile)
	if err != nil {
		log.Fatalf("❌ Ошибка чтения файла %s: %v", inputFile, err)
	}

	fmt.Printf("📄 Читаю файл: %s\n", inputFile)

	lines := strings.Split(string(data), "\n")
	var outputLines []string
	proxyCount := 0

	for _, line := range lines {
		trimmed := strings.TrimSpace(line)

		if strings.Contains(trimmed, "name:") &&
			strings.Contains(trimmed, "type:") &&
			strings.Contains(trimmed, "server:") &&
			strings.Contains(trimmed, "port:") &&
			strings.Contains(trimmed, "password:") {

			if !strings.Contains(trimmed, "skip-cert-verify:") {
				if strings.HasSuffix(trimmed, "}") {
					lineWithoutBrace := strings.TrimSuffix(strings.TrimSpace(line), "}")
					line = lineWithoutBrace + ", skip-cert-verify: true }"
				} else if strings.HasSuffix(trimmed, "},") {
					lineWithoutBrace := strings.TrimSuffix(strings.TrimSpace(line), "},")
					line = lineWithoutBrace + ", skip-cert-verify: true },"
				}
				proxyCount++
			}
		}

		outputLines = append(outputLines, line)
	}

	outputData := strings.Join(outputLines, "\n")

	err = os.WriteFile(outputFile, []byte(outputData), 0644)
	if err != nil {
		log.Fatalf("❌ Ошибка записи файла %s: %v", outputFile, err)
	}

	absOutputPath, _ := filepath.Abs(outputFile)
	absInputPath, _ := filepath.Abs(inputFile)

	fmt.Printf("✅ Обработано прокси: %d\n", proxyCount)
	fmt.Printf("✅ Готовый файл создан: %s\n", absOutputPath)
	fmt.Println("\n📋 Инструкция:")
	fmt.Printf("1. Исходный файл: %s\n", absInputPath)
	fmt.Printf("2. Результат: %s\n", absOutputPath)
	fmt.Println("3. Используйте x509_fixed.yaml в вашем клиенте")

	if proxyCount == 0 {
		fmt.Println("\n⚠️  Внимание: Не найдено прокси для обработки!")
		fmt.Println("   Убедитесь, что в файле x509_no_fix.yaml есть строки вида:")
		fmt.Println("   - { name: Name, type: trojan, server: example.com, port: 443, password: pass }")
	}

	fmt.Println("\nНажмите Enter для выхода...")
	fmt.Scanln()
}
