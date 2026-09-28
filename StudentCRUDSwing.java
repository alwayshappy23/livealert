import javax.swing.*;
import javax.swing.table.DefaultTableModel;
import java.awt.*;
import java.util.ArrayList;

class Student {
    int id;
    String name;
    int age;

    Student(int id, String name, int age) {
        this.id = id;
        this.name = name;
        this.age = age;
    }
}

public class StudentCRUDSwing extends JFrame {

    static ArrayList<Student> students = new ArrayList<>();
    static DefaultTableModel model;
    static JTable table;

    JTextField idField, nameField, ageField;

    public StudentCRUDSwing() {
        setTitle("Student Management System");
        setSize(600, 450);
        setDefaultCloseOperation(EXIT_ON_CLOSE);
        setLocationRelativeTo(null);
        setLayout(new BorderLayout());

        // ---- Input Panel ----
        JPanel inputPanel = new JPanel(new GridLayout(4, 2, 10, 10));
        inputPanel.setBorder(BorderFactory.createEmptyBorder(10, 10, 10, 10));

        inputPanel.add(new JLabel("ID:"));
        idField = new JTextField();
        inputPanel.add(idField);

        inputPanel.add(new JLabel("Name:"));
        nameField = new JTextField();
        inputPanel.add(nameField);

        inputPanel.add(new JLabel("Age:"));
        ageField = new JTextField();
        inputPanel.add(ageField);

        JLabel tip = new JLabel("(Select a row to Update/Delete)");
        tip.setForeground(Color.GRAY);
        inputPanel.add(tip);

        add(inputPanel, BorderLayout.NORTH);

        // ---- Table ----
        model = new DefaultTableModel(new String[]{"ID", "Name", "Age"}, 0);
        table = new JTable(model);
        JScrollPane scrollPane = new JScrollPane(table);
        add(scrollPane, BorderLayout.CENTER);

        // Row click -> fill text fields
        table.getSelectionModel().addListSelectionListener(e -> {
            int row = table.getSelectedRow();
            if (row >= 0) {
                idField.setText(model.getValueAt(row, 0).toString());
                nameField.setText(model.getValueAt(row, 1).toString());
                ageField.setText(model.getValueAt(row, 2).toString());
            }
        });

        // ---- Button Panel ----
        JPanel buttonPanel = new JPanel(new FlowLayout());

        JButton addBtn = new JButton("Add");
        JButton updateBtn = new JButton("Update");
        JButton deleteBtn = new JButton("Delete");
        JButton clearBtn = new JButton("Clear");

        buttonPanel.add(addBtn);
        buttonPanel.add(updateBtn);
        buttonPanel.add(deleteBtn);
        buttonPanel.add(clearBtn);

        add(buttonPanel, BorderLayout.SOUTH);

        // ---- Actions ----
        addBtn.addActionListener(e -> addStudent());
        updateBtn.addActionListener(e -> updateStudent());
        deleteBtn.addActionListener(e -> deleteStudent());
        clearBtn.addActionListener(e -> clearFields());
    }

    static void refreshTable() {
        model.setRowCount(0);
        for (Student s : students) {
            model.addRow(new Object[]{s.id, s.name, s.age});
        }
    }

    void clearFields() {
        idField.setText("");
        nameField.setText("");
        ageField.setText("");
        table.clearSelection();
    }

    void addStudent() {
        try {
            int id = Integer.parseInt(idField.getText().trim());
            String name = nameField.getText().trim();
            int age = Integer.parseInt(ageField.getText().trim());

            for (Student s : students) {
                if (s.id == id) {
                    JOptionPane.showMessageDialog(this, "ID already exists!");
                    return;
                }
            }

            students.add(new Student(id, name, age));
            refreshTable();
            clearFields();
            JOptionPane.showMessageDialog(this, "Student added successfully!");
        } catch (NumberFormatException ex) {
            JOptionPane.showMessageDialog(this, "Please enter valid ID and Age!");
        }
    }

    void updateStudent() {
        int row = table.getSelectedRow();
        if (row < 0) {
            JOptionPane.showMessageDialog(this, "Select a row to update!");
            return;
        }
        try {
            int id = Integer.parseInt(idField.getText().trim());
            String name = nameField.getText().trim();
            int age = Integer.parseInt(ageField.getText().trim());

            for (Student s : students) {
                if (s.id == id) {
                    s.name = name;
                    s.age = age;
                    refreshTable();
                    clearFields();
                    JOptionPane.showMessageDialog(this, "Student updated successfully!");
                    return;
                }
            }
            JOptionPane.showMessageDialog(this, "Student not found!");
        } catch (NumberFormatException ex) {
            JOptionPane.showMessageDialog(this, "Please enter valid ID and Age!");
        }
    }

    void deleteStudent() {
        int row = table.getSelectedRow();
        if (row < 0) {
            JOptionPane.showMessageDialog(this, "Select a row to delete!");
            return;
        }
        int id = Integer.parseInt(model.getValueAt(row, 0).toString());
        int confirm = JOptionPane.showConfirmDialog(this, "Delete student ID " + id + "?", "Confirm", JOptionPane.YES_NO_OPTION);
        if (confirm == JOptionPane.YES_OPTION) {
            students.removeIf(s -> s.id == id);
            refreshTable();
            clearFields();
            JOptionPane.showMessageDialog(this, "Student deleted successfully!");
        }
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> new StudentCRUDSwing().setVisible(true));
    }
}