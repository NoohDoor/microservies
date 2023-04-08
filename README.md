# Projektmanagement-Anwendung
Dieses Projekt ist eine Projektmanagement-Anwendung, die auf der Microservices-Architektur und Domain-driven Design (DDD) basiert. Die Anwendung ermöglicht es Benutzern, Projekte und Aufgaben zu erstellen, zu bearbeiten und zu verwalten, sowie Benachrichtigungen zu erhalten und nach Projekten, Aufgaben und Benutzern zu suchen.

## Inhaltsverzeichnis
- Services
- Technologien
- Probleme und Lösungen
- Zusätzliche Funktionen und Verbesserungen
- Installation 
- API-Dokumentation

## Services

Die Anwendung besteht aus den folgenden Microservices (beide aktuelle nur als Monolith vorhanden):

- Benutzer-Service: Authentifizierung, Autorisierung und Verwaltung von Benutzerinformationen.
- Aufgaben-Service: Verwaltung von Aufgabeninformationen, Erstellung von Aufgaben, Zuweisung von Benutzern zu Aufgaben und Bearbeitung von Aufgabendetails.

Geplant sind noch: 

- Projekt-Service: Verwaltung von Projektinformationen, Erstellung von Projekten, Zuweisung von Benutzern zu Projekten und Bearbeitung von Projektdetails.
- Benachrichtigungs-Service: Senden von Benachrichtigungen an Benutzer bei bestimmten Ereignissen, z.B. bei der Erstellung neuer Aufgaben oder der Zuweisung von Benutzern zu Aufgaben.
- Such-Service: Implementierung der Suchfunktion für die Anwendung, um Benutzern das schnelle Auffinden von Aufgaben oder Benutzern zu ermöglichen.

## Technologien
Die Anwendung verwendet die folgenden Technologien:

- Mircoservices: Python für die Backend-Entwicklung.
- Datenbanken: SQLite-DB
- API-Gateway: FastAPI

Geplante Technologien für eine richtige Anwendung:

- Microservices: Node.js (mit Express) für die Backend-Entwicklung.
- Container-Orchestrierung: Kubernetes (geplant auch für unsere Lite Version, aber zeitlich nicht geschafft).
- Datenbanken: PostgreSQL für relationale Daten und MongoDB für NoSQL-Daten.
- Messaging-System: RabbitMQ für die Kommunikation zwischen den Microservices.
- API-Gateway: NginX als Reverse Proxy und Load Balancer.

## Probleme und Lösungen

Beim aktuellen Projekt:

- Zuordung durch ForeignKey: Da wir zwei verschiedene SQLite-DB hatten wollten Funktionen wie POST /task nicht funktionieren da diese mit der UserID als ForeignKey auf die andere Datenbank referenzieren wollte.
- Authorisierung: Probleme beim erstellen eines Token da wir Anfangs Verständnisprobleme mit JWT hatten.
- POST /task: Es gab mehrere Probleme welche das Ausführen der Funktionen nicht möglich gemacht haben. 1. Entschlüsselung des Token und zuordnen von User (ID war expected, E-Mail wurde übergeben) 2. due_date hatte Probleme wegen Formatierung.

Bei einem ausgereiften Projekt:

- Datenkonsistenz: Verwendung von Event-driven Architektur und Messaging-Systemen (z.B. RabbitMQ) zur Verbesserung der Kommunikation zwischen den Microservices und zur Vereinfachung der Synchronisation von Daten.
- Transaktionsmanagement: Implementierung von verteilten Transaktionen und Saga-Mustern, um Transaktionsmanagement über verschiedene Microservices und Datenbanken hinweg zu ermöglichen.
- Performance: Implementierung von Caching-Mechanismen und Optimierung von Datenbankanfragen zur Verbesserung der Performance.

## Zusätzliche Funktionen und Verbesserungen

- Orchestrierung durch Kubernetes.
- Eine Benutzeroberfläche zur Bedienung der Anwendung.
- Bessere Datenbanklösung und Integration.
- Bugfixing und Stabilitätsverbesserungen.
- Integration von E-Mail-Benachrichtigungen, SMS oder Push-Benachrichtigungen.
- Erweiterung der Suchfunktionen.

## Installation
Um die Anwendung zu installieren und zu nutzen, befolgen Sie die folgenden Schritte:

### Voraussetzungen

Ein Umgebung haben welche die Libs aus der requirements-Datei beinhaltet.

### Schritte zur Installation

- Repository klonen: Klonen Sie das GitHub-Repository des Projekts auf Ihren lokalen Rechner.
- Dienst starten: taskmgm.py in der gewünschten Umgebung starten mit: uvicorn taskmgm:app --reload 
- Anwendung testen: Über 127.0.0.1:8000/docs sind die API Zugriffe erreichbar 

## API-Dokumentation

Die API-Endpunkte für die verschiedenen Microservices sind wie folgt:

### Derzeit vorhanden:


Benutzer-Service:
- POST /users: Erstellen eines neuen Benutzers.
- POST /token: Erstellt einen Token für aktuellen Benutzer. ( Bitte E-Mail als Username angeben ).
- GET /users: Auflisten aller Benutzer.
- GET /users/id: Abrufen der Informationen eines bestimmten Benutzers.
- PUT /users/id: Aktualisieren der Informationen eines bestimmten Benutzers.
- DELETE /users/id: Löschen eines bestimmten Benutzers.


Aufgaben-Service:
- POST /tasks: Erstellen einer neuen Aufgabe. ( Zu beachten ist die Formattierung für due_Date ( 'YYYY-MM-DDTHH:MM:SS' ).
- GET /tasks: Auflisten aller Aufgaben.
- GET /tasks/id: Abrufen der Informationen einer bestimmten Aufgabe.
- PUT /tasks/id: Aktualisieren der Informationen einer bestimmten Aufgabe.
- DELETE /tasks/id: Löschen einer bestimmten Aufgabe.

### Geplante Service:


Projekt-Service:
- POST /projects: Erstellen eines neuen Projekts.
- GET /projects: Auflisten aller Projekte.
- GET /projects/id: Abrufen der Informationen eines bestimmten Projekts.
- PUT /projects/id: Aktualisieren der Informationen eines bestimmten Projekts.
- DELETE /projects/id: Löschen eines bestimmten Projekts.


Benachrichtigungs-Service:
- POST /notifications: Erstellen einer neuen Benachrichtigung.
- GET /notifications: Auflisten aller Benachrichtigungen.
- GET /notifications/id: Abrufen der Informationen einer bestimmten Benachrichtigung.
- PUT /notifications/id: Aktualisieren der Informationen einer bestimmten Benachrichtigung.
- DELETE /notifications/id: Löschen einer bestimmten Benachrichtigung.


Such-Service:
- GET /search/users?q=<query>: Suchen von Benutzern basierend auf dem angegebenen Suchbegriff.
- GET /search/projects?q=<query>: Suchen von Projekten basierend auf dem angegebenen Suchbegriff.
- GET /search/tasks?q=<query>: Suchen von Aufgaben basierend auf dem angegebenen Suchbegriff.
