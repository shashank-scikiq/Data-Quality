package main

import (
	"fmt"
	"net/http"
)

const portNumber = ":8084"

// Home is the handler function for Homepage.
func Home(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintf(w, "This is a Home Page.")
}

// About is the handler function for About Page.
func About(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintf(w, "This is an about Page.")
	fmt.Println("About Called.")
}

// Sum adds two numbers and displays it on screen.
func Sum(w http.ResponseWriter, r *http.Request) {
	resp, err := addValues(2, 3)
	if err != nil {
		fmt.Fprintf(w, "Error")
	} else {
		_, _ = fmt.Fprintf(w, fmt.Sprintf("%d", resp))
	}
	fmt.Println("Sum Called.")
}

func addValues(x, y int) (int, error) {
	// var sum int
	sum := x + y
	return sum, nil
}

func main() {
	http.HandleFunc("/", Home)
	http.HandleFunc("/about", About)
	http.HandleFunc("/add", Sum)
	fmt.Printf("Starting Application on port %s", portNumber)
	_ = http.ListenAndServe(portNumber, nil)
}
